#pragma once

#include <cstddef>
#include <string>

// Orhun dilinin token türleri.
// v0.8 ile sınıf/OOP anahtar kelimeleri de ANAHTAR_KELIME altında taşınır.
enum class TokenType {
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
struct Token {
    TokenType tur;
    std::string deger;
    std::size_t satir;
};
