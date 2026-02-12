#pragma once

#include <cstdint>

// VM'de tasinan runtime degeri.
// Faz 2 ile birlikte std::variant yerine etiketli birlik (tagged union)
// kullaniyoruz. Karmaşık tipler heap'te Obj* olarak tutulur.
struct Obj;

enum class ValueType : std::uint8_t {
  BOS = 0,
  SAYI,
  MANTIK,
  NESNE,
};

struct Value {
  ValueType type = ValueType::BOS;
  union As {
    double sayi;
    bool mantik;
    Obj* nesne;
    As() : sayi(0.0) {}
  } as;

  static Value bos() {
    Value v;
    v.type = ValueType::BOS;
    v.as.sayi = 0.0;
    return v;
  }

  static Value sayi(double deger) {
    Value v;
    v.type = ValueType::SAYI;
    v.as.sayi = deger;
    return v;
  }

  static Value mantik(bool deger) {
    Value v;
    v.type = ValueType::MANTIK;
    v.as.mantik = deger;
    return v;
  }

  static Value nesne(Obj* deger) {
    Value v;
    v.type = ValueType::NESNE;
    v.as.nesne = deger;
    return v;
  }

  bool bosMu() const { return type == ValueType::BOS; }
  bool sayiMi() const { return type == ValueType::SAYI; }
  bool mantikMi() const { return type == ValueType::MANTIK; }
  bool nesneMi() const { return type == ValueType::NESNE; }
};

// Eski kodla uyumluluk icin.
using VMValue = Value;
