#include "Lexer.h"

#include <algorithm>
#include <cctype>
#include <cstdlib>
#include <unordered_set>
#include <vector>

namespace {
bool g_turkceKatiVarsayilan = false;

bool ortamDegiskeniAcik(const char *ad) {
  const char *ham = std::getenv(ad);
  if (ham == nullptr) {
    return false;
  }
  std::string deger(ham);
  std::transform(deger.begin(), deger.end(), deger.begin(),
                 [](unsigned char c) {
                   return static_cast<char>(std::tolower(c));
                 });
  return !(deger.empty() || deger == "0" || deger == "false" ||
           deger == "off" || deger == "hayir" || deger == "no");
}
} // namespace

Lexer::Lexer(const std::string &kaynakKodUtf8, bool turkceKati)
    : kaynakKod_(utf8ToU32(kaynakKodUtf8)) {
  turkceKati_ = turkceKati || turkceKatiVarsayilan() || ortamTurkceKatiAktif();
  // Bazı editörler dosya başına UTF-8 BOM ekleyebilir.
  if (!kaynakKod_.empty() && kaynakKod_.front() == U'\uFEFF') {
    kaynakKod_.erase(kaynakKod_.begin());
  }
}

void Lexer::setTurkceKatiVarsayilan(bool aktif) {
  g_turkceKatiVarsayilan = aktif;
}

bool Lexer::turkceKatiVarsayilan() { return g_turkceKatiVarsayilan; }

bool Lexer::ortamTurkceKatiAktif() {
  return ortamDegiskeniAcik("ORHUN_TURKCE_KATI");
}

std::vector<OrhunToken> Lexer::tokenize() {
  std::vector<OrhunToken> tokenlar;
  auto tokenEkle = [&](TokenTuru tur, const std::string &deger,
                       std::size_t satir, std::size_t sutun) {
    tokenlar.push_back({tur, deger, satir, sutun});
  };

  // Python benzeri blok yapısı için girinti seviyelerini yığında tutuyoruz.
  std::vector<int> girintiYigini = {0};
  bool satirBasi = true;

  while (!dosyaSonu()) {
    if (satirBasi) {
      int girintiSayisi = 0;

      // Satır başındaki boşlukları ölç.
      while (!dosyaSonu()) {
        const char32_t c = bak();
        if (c == U' ') {
          ilerle();
          ++girintiSayisi;
          continue;
        }
        if (c == U'\t') {
          ilerle();
          girintiSayisi += 4;
          continue;
        }
        break;
      }

      if (dosyaSonu()) {
        break;
      }

      const char32_t c = bak();

      // Boş satır ve yorum satırı girinti üretmez.
      if (c != U'\n' && c != U'\r' && c != U'#') {
        const int mevcutGirinti = girintiYigini.back();
        if (girintiSayisi > mevcutGirinti) {
          girintiYigini.push_back(girintiSayisi);
          tokenEkle(TokenTuru::GIRINTI, "<GIRINTI>", satir_, sutun_);
        } else if (girintiSayisi < mevcutGirinti) {
          while (girintiYigini.size() > 1 &&
                 girintiSayisi < girintiYigini.back()) {
            girintiYigini.pop_back();
            tokenEkle(TokenTuru::CIKINTI, "<CIKINTI>", satir_, sutun_);
          }
          if (girintiSayisi != girintiYigini.back()) {
            tokenEkle(TokenTuru::HATA, "Geçersiz girinti seviyesi", satir_,
                      sutun_);
            tokenEkle(TokenTuru::DOSYA_SONU, "", satir_, sutun_);
            return tokenlar;
          }
        }
      }

      satirBasi = false;
    }

    const char32_t c = bak();

    // Satır içi boşlukları geç.
    if (c == U' ' || c == U'\t' || c == U'\v' || c == U'\f') {
      ilerle();
      continue;
    }

    // # ile başlayan yorumları satır sonuna kadar tamamen yoksay.
    if (c == U'#') {
      yorumSatiriAtla();
      continue;
    }

    if (c == U'\r') {
      const std::size_t mevcutSatir = satir_;
      const std::size_t mevcutSutun = sutun_;
      ilerle();
      if (!dosyaSonu() && bak() == U'\n') {
        ilerle();
      }
      tokenEkle(TokenTuru::YENI_SATIR, "\\n", mevcutSatir, mevcutSutun);
      ++satir_;
      sutun_ = 1;
      satirBasi = true;
      continue;
    }

    if (c == U'\n') {
      const std::size_t mevcutSatir = satir_;
      const std::size_t mevcutSutun = sutun_;
      ilerle();
      tokenEkle(TokenTuru::YENI_SATIR, "\\n", mevcutSatir, mevcutSutun);
      ++satir_;
      sutun_ = 1;
      satirBasi = true;
      continue;
    }

    if (c == U'"') {
      tokenlar.push_back(metin());
      continue;
    }

    if (rakamMi(c)) {
      tokenlar.push_back(sayi());
      continue;
    }

    if (kimlikBaslangiciMi(c)) {
      tokenlar.push_back(kimlikVeyaAnahtarKelime());
      continue;
    }

    if (operatorMu(c) || c == U'%' || c == U'=' || c == U'>' || c == U'(' ||
        c == U')' || c == U'[' || c == U']' || c == U',' || c == U':' ||
        c == U'{' || c == U'}' || c == U'.' || c == U'?') {
      const std::size_t baslangicSutun = sutun_;
      const std::u32string tekKarakter(1, ilerle());
      tokenEkle(TokenTuru::ISLEM, u32ToUtf8(tekKarakter), satir_,
                baslangicSutun);
      continue;
    }

    // Desteklenmeyen karakterleri hata token'ına çevir.
    const std::size_t baslangicSutun = sutun_;
    const std::u32string tekKarakter(1, ilerle());
    tokenEkle(TokenTuru::HATA, "Tanımsız karakter: " + u32ToUtf8(tekKarakter),
              satir_, baslangicSutun);
  }

  // Dosya sonunda açık bloklar otomatik kapatılır.
  while (girintiYigini.size() > 1) {
    girintiYigini.pop_back();
    tokenEkle(TokenTuru::CIKINTI, "<CIKINTI>", satir_, sutun_);
  }

  tokenEkle(TokenTuru::DOSYA_SONU, "", satir_, sutun_);
  return tokenlar;
}

std::u32string Lexer::utf8ToU32(const std::string &metin) {
  std::u32string sonuc;
  std::size_t i = 0;

  while (i < metin.size()) {
    const unsigned char b0 = static_cast<unsigned char>(metin[i]);
    char32_t kodNoktasi = 0;
    std::size_t uzunluk = 0;

    if ((b0 & 0x80) == 0x00) {
      kodNoktasi = b0;
      uzunluk = 1;
    } else if ((b0 & 0xE0) == 0xC0) {
      if (i + 1 >= metin.size()) {
        sonuc.push_back(U'\uFFFD');
        break;
      }
      const unsigned char b1 = static_cast<unsigned char>(metin[i + 1]);
      if ((b1 & 0xC0) != 0x80) {
        sonuc.push_back(U'\uFFFD');
        ++i;
        continue;
      }
      kodNoktasi = (static_cast<char32_t>(b0 & 0x1F) << 6) |
                   static_cast<char32_t>(b1 & 0x3F);
      uzunluk = 2;
    } else if ((b0 & 0xF0) == 0xE0) {
      if (i + 2 >= metin.size()) {
        sonuc.push_back(U'\uFFFD');
        break;
      }
      const unsigned char b1 = static_cast<unsigned char>(metin[i + 1]);
      const unsigned char b2 = static_cast<unsigned char>(metin[i + 2]);
      if ((b1 & 0xC0) != 0x80 || (b2 & 0xC0) != 0x80) {
        sonuc.push_back(U'\uFFFD');
        ++i;
        continue;
      }
      kodNoktasi = (static_cast<char32_t>(b0 & 0x0F) << 12) |
                   (static_cast<char32_t>(b1 & 0x3F) << 6) |
                   static_cast<char32_t>(b2 & 0x3F);
      uzunluk = 3;
    } else if ((b0 & 0xF8) == 0xF0) {
      if (i + 3 >= metin.size()) {
        sonuc.push_back(U'\uFFFD');
        break;
      }
      const unsigned char b1 = static_cast<unsigned char>(metin[i + 1]);
      const unsigned char b2 = static_cast<unsigned char>(metin[i + 2]);
      const unsigned char b3 = static_cast<unsigned char>(metin[i + 3]);
      if ((b1 & 0xC0) != 0x80 || (b2 & 0xC0) != 0x80 || (b3 & 0xC0) != 0x80) {
        sonuc.push_back(U'\uFFFD');
        ++i;
        continue;
      }
      kodNoktasi = (static_cast<char32_t>(b0 & 0x07) << 18) |
                   (static_cast<char32_t>(b1 & 0x3F) << 12) |
                   (static_cast<char32_t>(b2 & 0x3F) << 6) |
                   static_cast<char32_t>(b3 & 0x3F);
      uzunluk = 4;
    } else {
      sonuc.push_back(U'\uFFFD');
      ++i;
      continue;
    }

    sonuc.push_back(kodNoktasi);
    i += uzunluk;
  }

  return sonuc;
}

std::string Lexer::u32ToUtf8(const std::u32string &metin) {
  std::string sonuc;

  for (const char32_t cp : metin) {
    if (cp <= 0x7F) {
      sonuc.push_back(static_cast<char>(cp));
    } else if (cp <= 0x7FF) {
      sonuc.push_back(static_cast<char>(0xC0 | ((cp >> 6) & 0x1F)));
      sonuc.push_back(static_cast<char>(0x80 | (cp & 0x3F)));
    } else if (cp <= 0xFFFF) {
      sonuc.push_back(static_cast<char>(0xE0 | ((cp >> 12) & 0x0F)));
      sonuc.push_back(static_cast<char>(0x80 | ((cp >> 6) & 0x3F)));
      sonuc.push_back(static_cast<char>(0x80 | (cp & 0x3F)));
    } else {
      sonuc.push_back(static_cast<char>(0xF0 | ((cp >> 18) & 0x07)));
      sonuc.push_back(static_cast<char>(0x80 | ((cp >> 12) & 0x3F)));
      sonuc.push_back(static_cast<char>(0x80 | ((cp >> 6) & 0x3F)));
      sonuc.push_back(static_cast<char>(0x80 | (cp & 0x3F)));
    }
  }

  return sonuc;
}

bool Lexer::dosyaSonu() const { return konum_ >= kaynakKod_.size(); }

char32_t Lexer::bak() const {
  if (dosyaSonu()) {
    return U'\0';
  }
  return kaynakKod_[konum_];
}

char32_t Lexer::bakIleri(std::size_t uzaklik) const {
  const std::size_t hedef = konum_ + uzaklik;
  if (hedef >= kaynakKod_.size()) {
    return U'\0';
  }
  return kaynakKod_[hedef];
}

char32_t Lexer::ilerle() {
  if (dosyaSonu()) {
    return U'\0';
  }
  ++sutun_;
  return kaynakKod_[konum_++];
}

OrhunToken Lexer::kimlikVeyaAnahtarKelime() {
  const std::size_t baslangicSatir = satir_;
  const std::size_t baslangicSutun = sutun_;
  std::u32string yazi;
  yazi.push_back(ilerle());

  while (!dosyaSonu() && kimlikKarakteriMi(bak())) {
    yazi.push_back(ilerle());
  }

  const std::string deger = u32ToUtf8(yazi);
  if (anahtarKelimeMi(yazi)) {
    return {TokenTuru::ANAHTAR_KELIME, deger, baslangicSatir, baslangicSutun};
  }
  return {TokenTuru::KIMLIK, deger, baslangicSatir, baslangicSutun};
}

OrhunToken Lexer::sayi() {
  const std::size_t baslangicSatir = satir_;
  const std::size_t baslangicSutun = sutun_;
  std::u32string yazi;
  bool noktaGoruldu = false;

  while (!dosyaSonu()) {
    const char32_t c = bak();
    if (rakamMi(c)) {
      yazi.push_back(ilerle());
      continue;
    }

    // Ondalık destek: sadece bir kez ve ardından en az bir rakam varsa.
    if (c == U'.' && !noktaGoruldu && rakamMi(bakIleri(1))) {
      noktaGoruldu = true;
      yazi.push_back(ilerle());
      continue;
    }

    break;
  }

  return {noktaGoruldu ? TokenTuru::ONDALIK : TokenTuru::SAYI, u32ToUtf8(yazi),
          baslangicSatir, baslangicSutun};
}

OrhunToken Lexer::metin() {
  const std::size_t baslangicSatir = satir_;
  const std::size_t baslangicSutun = sutun_;
  std::u32string icerik;

  // Açılış tırnağını tüket.
  ilerle();

  while (!dosyaSonu()) {
    const char32_t c = ilerle();

    if (c == U'"') {
      return {TokenTuru::METIN, u32ToUtf8(icerik), baslangicSatir,
              baslangicSutun};
    }

    // Basit kaçış dizileri desteği.
    if (c == U'\\' && !dosyaSonu()) {
      const char32_t k = ilerle();
      if (k == U'"') {
        icerik.push_back(U'"');
        continue;
      }
      if (k == U'\\') {
        icerik.push_back(U'\\');
        continue;
      }
      if (k == U'n') {
        icerik.push_back(U'\n');
        continue;
      }
      if (k == U't') {
        icerik.push_back(U'\t');
        continue;
      }
      icerik.push_back(k);
      continue;
    }

    if (c == U'\n' || c == U'\r') {
      return {TokenTuru::HATA, "Kapanmayan metin sabiti", baslangicSatir,
              baslangicSutun};
    }

    icerik.push_back(c);
  }

  return {TokenTuru::HATA, "Kapanmayan metin sabiti", baslangicSatir,
          baslangicSutun};
}

bool Lexer::rakamMi(char32_t c) const { return c >= U'0' && c <= U'9'; }

bool Lexer::kimlikBaslangiciMi(char32_t c) const {
  const bool asciiHarf = (c >= U'a' && c <= U'z') || (c >= U'A' && c <= U'Z');
  return c == U'_' || asciiHarf || turkceHarfMi(c);
}

bool Lexer::kimlikKarakteriMi(char32_t c) const {
  return kimlikBaslangiciMi(c) || rakamMi(c);
}

bool Lexer::turkceHarfMi(char32_t c) const {
  switch (c) {
  case U'ç':
  case U'Ç':
  case U'ğ':
  case U'Ğ':
  case U'ı':
  case U'I':
  case U'İ':
  case U'ö':
  case U'Ö':
  case U'ş':
  case U'Ş':
  case U'ü':
  case U'Ü':
    return true;
  default:
    return false;
  }
}

bool Lexer::operatorMu(char32_t c) const {
  return c == U'+' || c == U'-' || c == U'*' || c == U'/' || c == U'%';
}

bool Lexer::anahtarKelimeMi(const std::u32string &metin) const {
  static const std::unordered_set<std::u32string> anahtarKelimeler = {
      U"yazdır", U"olsun",     U"eğer",       U"ise",    U"değilse",
      U"doğru",  U"yanlış",    U"tekrarla",   U"kez",    U"sor",
      U"işlev",  U"dış_işlev", U"döndür",     U"dahil_et",
      U"sürece", U"eşit",      U"eşit_değil", U"büyük",  U"küçük",
      U"ve",     U"veya",      U"değil",      U"tip",    U"yeni",
      U"benim",  U"deneme",    U"yakala",     U"kır",    U"devam",
      U"ust",    U"her",       U"için",       U"içinde", U"paralel",
      U"yap"};
  static const std::unordered_set<std::u32string> aliasAnahtarKelimeler = {
      U"dis_islev"};

  if (anahtarKelimeler.find(metin) != anahtarKelimeler.end()) {
    return true;
  }
  if (turkceKati_) {
    return false;
  }
  return aliasAnahtarKelimeler.find(metin) != aliasAnahtarKelimeler.end();
}

void Lexer::yorumSatiriAtla() {
  while (!dosyaSonu()) {
    const char32_t c = bak();
    if (c == U'\n' || c == U'\r') {
      break;
    }
    ilerle();
  }
}
