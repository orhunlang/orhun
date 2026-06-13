#pragma once

#include <cstdint>
#include <string>

#ifdef _WIN32
#include <windows.h>
#else
#include <dlfcn.h>
#endif

namespace runtime {

// Platform bagimsiz dinamik kutuphane yukleyici.
class DynamicLibrary {
public:
  DynamicLibrary() = default;
  explicit DynamicLibrary(std::string yol) : yol_(std::move(yol)) {}

  DynamicLibrary(const DynamicLibrary&) = delete;
  DynamicLibrary& operator=(const DynamicLibrary&) = delete;

  DynamicLibrary(DynamicLibrary&& other) noexcept { tasin(std::move(other)); }
  DynamicLibrary& operator=(DynamicLibrary&& other) noexcept {
    if (this != &other) {
      close();
      tasin(std::move(other));
    }
    return *this;
  }

  ~DynamicLibrary() { close(); }

  void setPath(std::string yol) { yol_ = std::move(yol); }
  const std::string& path() const { return yol_; }

  bool load(std::string* hata = nullptr) {
    if (isLoaded()) {
      return true;
    }
    if (yol_.empty()) {
      if (hata) {
        *hata = "Kutuphane yolu bos.";
      }
      return false;
    }

#ifdef _WIN32
    handle_ = reinterpret_cast<void*>(LoadLibraryW(utf8ToWide(yol_).c_str()));
    if (!handle_) {
      if (hata) {
        *hata = sonHataMetni();
      }
      return false;
    }
#else
    handle_ = dlopen(yol_.c_str(), RTLD_LAZY);
    if (!handle_) {
      if (hata) {
        const char* dlHatasi = dlerror();
        *hata = dlHatasi != nullptr ? dlHatasi : "dlopen basarisiz.";
      }
      return false;
    }
#endif
    return true;
  }

  bool isLoaded() const { return handle_ != nullptr; }

  std::uintptr_t getSymbol(const std::string& ad,
                           std::string* hata = nullptr) const {
    if (!isLoaded()) {
      if (hata) {
        *hata = "Kutuphane yuklu degil.";
      }
      return 0;
    }

#ifdef _WIN32
    FARPROC p =
        GetProcAddress(reinterpret_cast<HMODULE>(handle_), ad.c_str());
    if (!p) {
      if (hata) {
        *hata = sonHataMetni();
      }
      return 0;
    }
    return reinterpret_cast<std::uintptr_t>(p);
#else
    dlerror(); // eski hatayi temizle
    void* p = dlsym(handle_, ad.c_str());
    const char* err = dlerror();
    if (err != nullptr) {
      if (hata) {
        *hata = err;
      }
      return 0;
    }
    return reinterpret_cast<std::uintptr_t>(p);
#endif
  }

  void close() {
    if (!isLoaded()) {
      return;
    }
#ifdef _WIN32
    FreeLibrary(reinterpret_cast<HMODULE>(handle_));
#else
    dlclose(handle_);
#endif
    handle_ = nullptr;
  }

private:
  std::string yol_;
  void* handle_ = nullptr;

  void tasin(DynamicLibrary&& other) {
    yol_ = std::move(other.yol_);
    handle_ = other.handle_;
    other.handle_ = nullptr;
  }

#ifdef _WIN32
  static std::wstring utf8ToWide(const std::string& s) {
    if (s.empty()) {
      return std::wstring();
    }
    const int n = MultiByteToWideChar(CP_UTF8, 0, s.c_str(),
                                      static_cast<int>(s.size()), nullptr, 0);
    if (n <= 0) {
      return std::wstring();
    }
    std::wstring out(static_cast<std::size_t>(n), L'\0');
    const int w = MultiByteToWideChar(CP_UTF8, 0, s.c_str(),
                                      static_cast<int>(s.size()), out.data(), n);
    if (w <= 0) {
      return std::wstring();
    }
    return out;
  }

  static std::string sonHataMetni() {
    const DWORD kod = GetLastError();
    LPSTR tampon = nullptr;
    const DWORD uzunluk = FormatMessageA(
        FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_FROM_SYSTEM |
            FORMAT_MESSAGE_IGNORE_INSERTS,
        nullptr, kod, MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT),
        reinterpret_cast<LPSTR>(&tampon), 0, nullptr);
    if (uzunluk == 0 || tampon == nullptr) {
      return "Win32 hata kodu: " + std::to_string(kod);
    }
    std::string mesaj(tampon, uzunluk);
    LocalFree(tampon);
    while (!mesaj.empty() &&
           (mesaj.back() == '\n' || mesaj.back() == '\r' ||
            mesaj.back() == ' ' || mesaj.back() == '\t')) {
      mesaj.pop_back();
    }
    return mesaj;
  }
#endif
};

} // namespace runtime
