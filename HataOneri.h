#pragma once

#include "Yardimci.h"

#include <optional>
#include <string>
#include <string_view>
#include <unordered_map>
#include <vector>

// Compiler as a Teacher: hatalara yalnızca "ne oldu" değil,
// "nasıl düzeltilir" ve "neden" satırları da ekler.
//
// Çıktı biçimi (Rust/Elm tarzı):
//   Satır N, Sütun M: ana mesaj [token: x]
//     Bunu mu demek istediniz: 'aday'?
//     İpucu: kısa açıklama.
//     Örnek: düzeltme örneği.

inline std::string hataSatiriEkle(const std::string &mesaj,
                                  const std::string &ipucu) {
  if (ipucu.empty()) {
    return mesaj;
  }
  return mesaj + "\n  " + ipucu;
}

inline std::string hataIpuclariEkle(const std::string &mesaj,
                                    const std::vector<std::string> &ipuclari) {
  std::string sonuc = mesaj;
  for (const std::string &ipucu : ipuclari) {
    if (!ipucu.empty()) {
      sonuc = hataSatiriEkle(sonuc, ipucu);
    }
  }
  return sonuc;
}

inline std::string ornekSatiri(const std::string &ornek) {
  return "Örnek: " + ornek;
}

inline std::string ipucuSatiri(const std::string &metin) {
  return "İpucu: " + metin;
}

// Yaygın İngilizce anahtar / yerleşik adları → Türkçe karşılıkları.
// Levenshtein önerisinden önce kontrol edilir ('if' → 'ise' değil, 'eğer').
inline const std::unordered_map<std::string, std::string> &
ingilizceTurkceKosesi() {
  static const std::unordered_map<std::string, std::string> kose = {
      {"if", "eğer"},
      {"else", "değilse"},
      {"elif", "eğer"},
      {"while", "sürece"},
      {"for", "her"},
      {"in", "içinde"},
      {"function", "işlev"},
      {"func", "işlev"},
      {"fn", "işlev"},
      {"def", "işlev"},
      {"return", "döndür"},
      {"print", "yazdır"},
      {"write", "yazdır"},
      {"println", "yazdır"},
      {"input", "oku"},
      {"read", "oku"},
      {"true", "doğru"},
      {"false", "yanlış"},
      {"and", "ve"},
      {"or", "veya"},
      {"not", "değil"},
      {"break", "kır"},
      {"continue", "devam"},
      {"try", "deneme"},
      {"catch", "yakala"},
      {"except", "yakala"},
      {"class", "tip"},
      {"struct", "tip"},
      {"type", "tip"},
      {"new", "yeni"},
      {"let", "olsun"},
      {"var", "olsun"},
      {"const", "olsun"},
      {"import", "dahil_et"},
      {"include", "dahil_et"},
      {"from", "dahil_et"},
      {"null", "bos"},
      {"none", "bos"},
      {"nil", "bos"},
      {"len", "uzunluk"},
      {"length", "uzunluk"},
      {"size", "uzunluk"},
  };
  return kose;
}

inline std::optional<std::string> ingilizceKarsiligi(std::string_view ad) {
  const auto &kose = ingilizceTurkceKosesi();
  const auto it = kose.find(std::string(ad));
  if (it == kose.end()) {
    return std::nullopt;
  }
  return it->second;
}

// Yalnızca gerçek Orhun anahtar kelimelerine karşılık gelen İngilizce aliaslar.
// Lexer, varsayılan modda bunları Türkçe anahtar kelimeye normalize eder.
// Türkçe katı modda alias reddedilir.
inline const std::unordered_map<std::string, std::string> &
ingilizceAnahtarAliasHaritasi() {
  static const std::unordered_map<std::string, std::string> harita = {
      {"if", "eğer"},
      {"else", "değilse"},
      {"while", "sürece"},
      {"for", "her"},
      {"in", "içinde"},
      {"function", "işlev"},
      {"return", "döndür"},
      {"print", "yazdır"},
      {"println", "yazdır"},
      {"write", "yazdır"},
      {"input", "sor"},
      {"true", "doğru"},
      {"false", "yanlış"},
      {"and", "ve"},
      {"or", "veya"},
      {"not", "değil"},
      {"break", "kır"},
      {"continue", "devam"},
      {"try", "deneme"},
      {"catch", "yakala"},
      {"except", "yakala"},
      {"class", "tip"},
      {"new", "yeni"},
      {"import", "dahil_et"},
      {"include", "dahil_et"},
  };
  return harita;
}

inline std::optional<std::string>
ingilizceAnahtarKarsiligi(std::string_view ad) {
  const auto &harita = ingilizceAnahtarAliasHaritasi();
  const auto it = harita.find(std::string(ad));
  if (it == harita.end()) {
    return std::nullopt;
  }
  return it->second;
}

// İngilizce köprü + dosya içi adaylar üzerinde akıllı öneri.
// İngilizce eşleşme varsa Levenshtein'e tercih edilir.
inline std::optional<std::string> gelismisOneriBul(
    std::string_view aranan, const std::vector<std::string> &adaylar) {
  if (aranan.empty()) {
    return std::nullopt;
  }
  if (const auto eng = ingilizceKarsiligi(aranan); eng.has_value()) {
    return eng;
  }
  const std::size_t maxMesafe =
      utf8KodNoktalarinaCevir(aranan).size() >= 7 ? 3 : 2;
  return enYakinOneri(aranan, adaylar, maxMesafe);
}

// Bilinen sözdizimi hataları için öğretici ipuçları.
inline std::vector<std::string> sozdizimiIpucu(const std::string &anahtar) {
  if (anahtar == "eksik-iki-nokta-islev") {
    return {
        ipucuSatiri("İşlev tanımı iki nokta ile biter."),
        ornekSatiri("işlev topla(a, b):"),
    };
  }
  if (anahtar == "eksik-iki-nokta-eger") {
    return {
        ipucuSatiri("'eğer' bloğu 'ise' ve iki nokta ile başlar."),
        ornekSatiri("eğer x > 0 ise:"),
    };
  }
  if (anahtar == "eksik-ise") {
    return {
        ipucuSatiri("Koşuldan sonra 'ise' ve iki nokta gelir."),
        ornekSatiri("eğer dogru ise:"),
    };
  }
  if (anahtar == "eksik-iki-nokta-surece") {
    return {
        ipucuSatiri("'sürece' döngüsü koşuldan sonra iki nokta ister."),
        ornekSatiri("sürece i < 10:"),
    };
  }
  if (anahtar == "eksik-iki-nokta-her") {
    return {
        ipucuSatiri("'her ... içinde' döngüsü iki nokta ile biter."),
        ornekSatiri("her oge içinde liste:"),
    };
  }
  if (anahtar == "eksik-iki-nokta-tip") {
    return {
        ipucuSatiri("Sınıf tanımı iki nokta ile başlar."),
        ornekSatiri("tip Nokta:"),
    };
  }
  if (anahtar == "eksik-iki-nokta-deneme") {
    return {
        ipucuSatiri("'deneme' ve 'yakala' blokları iki nokta ister."),
        ornekSatiri("deneme:"),
    };
  }
  if (anahtar == "eksik-parantez-islev") {
    return {
        ipucuSatiri("İşlev adından hemen sonra parantez açılır."),
        ornekSatiri("işlev f(a, b):"),
    };
  }
  if (anahtar == "ingilizce-anahtar") {
    return {
        ipucuSatiri(
            "Orhun Türkçe sözdizimi kullanır. İngilizce anahtar kelime "
            "yerine Türkçe karşılığını yazın."),
    };
  }
  if (anahtar == "tanimsiz-degisken") {
    return {
        ipucuSatiri("Değişkeni 'ad olsun deger' ile tanımlayın "
                    "veya adını kontrol edin."),
        ornekSatiri("sayi olsun 0"),
    };
  }
  if (anahtar == "tanimsiz-islev") {
    return {
        ipucuSatiri("İşlevi 'işlev ad():' ile tanımlayın "
                    "veya adını kontrol edin."),
        ornekSatiri("islev topla(a, b):"),
    };
  }
  return {};
}

// İngilizce anahtar kelime tespiti için öğretici satır.
inline std::optional<std::string> ingilizceAnahtarIpucu(std::string_view ad) {
  const auto karsilik = ingilizceKarsiligi(ad);
  if (!karsilik.has_value()) {
    return std::nullopt;
  }
  return ipucuSatiri("Orhun Türkçe sözdizimi kullanır; '" + std::string(ad) +
                     "' yerine '" + karsilik.value() + "' yazın.");
}

// Öğretici "Bunu mu demek istediniz" + İpucu/Örnek satırları üretir.
// İngilizce köprü eşleştiyse genel tanımlama ipuçları bastırılır.
inline std::string ogreticiOneriliMesaj(const std::string &mesaj,
                                        const std::string &aranan,
                                        const std::vector<std::string> &adaylar,
                                        const std::vector<std::string> &ipuclari) {
  std::string sonuc = mesaj;
  std::vector<std::string> birlesik;
  if (!aranan.empty()) {
    const auto eng = ingilizceKarsiligi(aranan);
    if (eng.has_value()) {
      sonuc += " Bunu mu demek istediniz: '" + eng.value() + "'?";
      if (const auto engIpucu = ingilizceAnahtarIpucu(aranan);
          engIpucu.has_value()) {
        birlesik.push_back(engIpucu.value());
      }
    } else {
      if (const auto oneri = enYakinOneri(
              aranan, adaylar,
              utf8KodNoktalarinaCevir(aranan).size() >= 7 ? 3 : 2);
          oneri.has_value()) {
        sonuc += " Bunu mu demek istediniz: '" + oneri.value() + "'?";
      }
      birlesik = ipuclari;
    }
  } else {
    birlesik = ipuclari;
  }
  return hataIpuclariEkle(sonuc, birlesik);
}
