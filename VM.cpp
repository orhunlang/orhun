#include "VM.h"

#include <cmath>
#include <iostream>
#include <limits>
#include <stdexcept>

void VM::sifirla() {
  chunk_ = nullptr;
  ip_ = 0;
  yigin_.clear();
  globaller_.clear();
}

void VM::calistir(const BytecodeChunk& chunk) {
  chunk_ = &chunk;
  ip_ = 0;
  yigin_.clear();

  while (ip_ < chunk_->kod.size()) {
    const OpCode op = static_cast<OpCode>(byteOku());
    switch (op) {
      case OpCode::OP_SABIT: {
        const std::uint16_t indeks = u16Oku();
        yiginPush(sabitOku(indeks));
        break;
      }
      case OpCode::OP_BOS:
        yiginPush(VMValue{});
        break;
      case OpCode::OP_DOGRU:
        yiginPush(VMValue(true));
        break;
      case OpCode::OP_YANLIS:
        yiginPush(VMValue(false));
        break;
      case OpCode::OP_POP:
        (void)yiginPop();
        break;
      case OpCode::OP_GET_GLOBAL: {
        const std::uint16_t indeks = u16Oku();
        const VMValue& adDegeri = sabitOku(indeks);
        if (!std::holds_alternative<std::string>(adDegeri.veri)) {
          calismaHatasi("GET_GLOBAL ad sabiti metin degil.");
        }
        const std::string& ad = std::get<std::string>(adDegeri.veri);
        const auto it = globaller_.find(ad);
        if (it == globaller_.end()) {
          calismaHatasi("Tanimsiz degisken: '" + ad + "'.");
        }
        yiginPush(it->second);
        break;
      }
      case OpCode::OP_SET_GLOBAL: {
        const std::uint16_t indeks = u16Oku();
        const VMValue& adDegeri = sabitOku(indeks);
        if (!std::holds_alternative<std::string>(adDegeri.veri)) {
          calismaHatasi("SET_GLOBAL ad sabiti metin degil.");
        }
        const std::string& ad = std::get<std::string>(adDegeri.veri);
        globaller_[ad] = yiginBak(0);
        break;
      }
      case OpCode::OP_TOPLA: {
        const VMValue sag = yiginPop();
        const VMValue sol = yiginPop();

        const bool solMetin = std::holds_alternative<std::string>(sol.veri);
        const bool sagMetin = std::holds_alternative<std::string>(sag.veri);
        if (solMetin || sagMetin) {
          yiginPush(VMValue(metneCevir(sol) + metneCevir(sag)));
          break;
        }

        const double sonuc = sayiyaCevir(sol, "toplama") + sayiyaCevir(sag, "toplama");
        yiginPush(VMValue(sonuc));
        break;
      }
      case OpCode::OP_CIKAR: {
        const double sag = sayiyaCevir(yiginPop(), "cikarma");
        const double sol = sayiyaCevir(yiginPop(), "cikarma");
        yiginPush(VMValue(sol - sag));
        break;
      }
      case OpCode::OP_CARP: {
        const double sag = sayiyaCevir(yiginPop(), "carpma");
        const double sol = sayiyaCevir(yiginPop(), "carpma");
        yiginPush(VMValue(sol * sag));
        break;
      }
      case OpCode::OP_BOL: {
        const double sag = sayiyaCevir(yiginPop(), "bolme");
        const double sol = sayiyaCevir(yiginPop(), "bolme");
        if (std::abs(sag) <= std::numeric_limits<double>::epsilon()) {
          calismaHatasi("Sifira bolme hatasi.");
        }
        yiginPush(VMValue(sol / sag));
        break;
      }
      case OpCode::OP_NEGATE: {
        const double deger = sayiyaCevir(yiginPop(), "isaret degistirme");
        yiginPush(VMValue(-deger));
        break;
      }
      case OpCode::OP_NOT: {
        const bool sonuc = falseMi(yiginPop());
        yiginPush(VMValue(sonuc));
        break;
      }
      case OpCode::OP_ESIT: {
        const VMValue sag = yiginPop();
        const VMValue sol = yiginPop();
        yiginPush(VMValue(esitMi(sol, sag)));
        break;
      }
      case OpCode::OP_BUYUK: {
        const double sag = sayiyaCevir(yiginPop(), "karsilastirma");
        const double sol = sayiyaCevir(yiginPop(), "karsilastirma");
        yiginPush(VMValue(sol > sag));
        break;
      }
      case OpCode::OP_KUCUK: {
        const double sag = sayiyaCevir(yiginPop(), "karsilastirma");
        const double sol = sayiyaCevir(yiginPop(), "karsilastirma");
        yiginPush(VMValue(sol < sag));
        break;
      }
      case OpCode::OP_VE: {
        const VMValue sag = yiginPop();
        const VMValue sol = yiginPop();
        yiginPush(VMValue(!falseMi(sol) && !falseMi(sag)));
        break;
      }
      case OpCode::OP_VEYA: {
        const VMValue sag = yiginPop();
        const VMValue sol = yiginPop();
        yiginPush(VMValue(!falseMi(sol) || !falseMi(sag)));
        break;
      }
      case OpCode::OP_YAZDIR: {
        const VMValue deger = yiginPop();
        std::cout << metneCevir(deger) << '\n';
        break;
      }
      case OpCode::OP_ATLA: {
        const std::uint16_t ofset = u16Oku();
        ip_ += ofset;
        break;
      }
      case OpCode::OP_ATLA_EGER_YANLIS: {
        const std::uint16_t ofset = u16Oku();
        if (falseMi(yiginBak(0))) {
          ip_ += ofset;
        }
        break;
      }
      case OpCode::OP_DONGU: {
        const std::uint16_t ofset = u16Oku();
        if (ip_ < ofset) {
          calismaHatasi("Gecersiz dongu geri atlamasi.");
        }
        ip_ -= ofset;
        break;
      }
      case OpCode::OP_DON:
        return;
    }
  }
}

void VM::yiginPush(VMValue deger) { yigin_.push_back(std::move(deger)); }

VMValue VM::yiginPop() {
  if (yigin_.empty()) {
    calismaHatasi("Yigin alttan tasma hatasi.");
  }
  VMValue son = yigin_.back();
  yigin_.pop_back();
  return son;
}

const VMValue& VM::yiginBak(std::size_t tersten) const {
  if (tersten >= yigin_.size()) {
    calismaHatasi("Yigin okunamadi (sinir disi).");
  }
  return yigin_[yigin_.size() - 1 - tersten];
}

std::uint8_t VM::byteOku() {
  if (chunk_ == nullptr || ip_ >= chunk_->kod.size()) {
    calismaHatasi("Bytecode sonu beklenmedik sekilde bitti.");
  }
  return chunk_->kod[ip_++];
}

std::uint16_t VM::u16Oku() {
  const std::uint8_t yuksek = byteOku();
  const std::uint8_t dusuk = byteOku();
  return static_cast<std::uint16_t>((static_cast<std::uint16_t>(yuksek) << 8) |
                                    static_cast<std::uint16_t>(dusuk));
}

const VMValue& VM::sabitOku(std::uint16_t indeks) const {
  if (chunk_ == nullptr || indeks >= chunk_->sabitler.size()) {
    calismaHatasi("Sabit indeksi gecersiz.");
  }
  return chunk_->sabitler[indeks];
}

bool VM::falseMi(const VMValue& deger) const {
  if (std::holds_alternative<std::monostate>(deger.veri)) {
    return true;
  }
  if (const auto* mantik = std::get_if<bool>(&deger.veri)) {
    return !(*mantik);
  }
  if (const auto* sayi = std::get_if<double>(&deger.veri)) {
    return std::abs(*sayi) <= std::numeric_limits<double>::epsilon();
  }
  if (const auto* metin = std::get_if<std::string>(&deger.veri)) {
    return metin->empty();
  }
  return false;
}

bool VM::esitMi(const VMValue& sol, const VMValue& sag) const {
  if (sol.veri.index() != sag.veri.index()) {
    return false;
  }
  if (std::holds_alternative<std::monostate>(sol.veri)) {
    return true;
  }
  if (const auto* solSayi = std::get_if<double>(&sol.veri)) {
    return *solSayi == std::get<double>(sag.veri);
  }
  if (const auto* solMetin = std::get_if<std::string>(&sol.veri)) {
    return *solMetin == std::get<std::string>(sag.veri);
  }
  if (const auto* solMantik = std::get_if<bool>(&sol.veri)) {
    return *solMantik == std::get<bool>(sag.veri);
  }
  return false;
}

std::string VM::metneCevir(const VMValue& deger) const {
  if (std::holds_alternative<std::monostate>(deger.veri)) {
    return "bos";
  }
  if (const auto* sayi = std::get_if<double>(&deger.veri)) {
    std::string metin = std::to_string(*sayi);
    while (!metin.empty() && metin.back() == '0') {
      metin.pop_back();
    }
    if (!metin.empty() && metin.back() == '.') {
      metin.pop_back();
    }
    return metin.empty() ? "0" : metin;
  }
  if (const auto* metin = std::get_if<std::string>(&deger.veri)) {
    return *metin;
  }
  if (const auto* mantik = std::get_if<bool>(&deger.veri)) {
    return *mantik ? "dogru" : "yanlis";
  }
  return "<deger>";
}

double VM::sayiyaCevir(const VMValue& deger, const std::string& baglam) const {
  if (const auto* sayi = std::get_if<double>(&deger.veri)) {
    return *sayi;
  }
  calismaHatasi("Sayisal olmayan deger ile " + baglam + " yapilamaz.");
}

[[noreturn]] void VM::calismaHatasi(const std::string& mesaj) const {
  std::size_t satir = 0;
  if (chunk_ != nullptr && ip_ > 0 && ip_ - 1 < chunk_->satirlar.size()) {
    satir = chunk_->satirlar[ip_ - 1];
  }
  throw std::runtime_error("VM Calisma Hatasi (satir " + std::to_string(satir) +
                           "): " + mesaj);
}

