#pragma once

#include <cstddef>
#include <string>

// Orhun dilinin token türleri.
// v1.0 ile ust/için/içinde anahtar kelimeleri de ANAHTAR_KELIME altında.
// Windows çakışmasını önlemek için 'TokenType' yerine 'TokenTuru'.
enum class TokenTuru {
  ANAHTAR_KELIME,
  KIMLIK,
  SAYI,
  ONDALIK,
  METIN,
  ISLEM,
  YENI_SATIR,
  GIRINTI,
  CIKINTI,
  DOSYA_SONU,
  HATA
};

// Lexer çıktısındaki tek bir parçayı (token) temsil eder.
// satir bilgisi hata mesajlarında doğrudan kullanıcıya gösterilir.
// 'Token' yerine 'OrhunToken' kullanıyoruz.
struct OrhunToken {
  TokenTuru tur;
  std::string deger;
  std::size_t satir;
  std::size_t sutun = 1;
};
