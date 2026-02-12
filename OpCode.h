#pragma once

#include <cstdint>

// Faz 1 Bytecode VM icin komut seti.
// Isimler Turkce tutuldu ki debug ederken okunabilir kalsin.
enum class OpCode : std::uint8_t {
  OP_SABIT = 0,
  OP_BOS,
  OP_DOGRU,
  OP_YANLIS,
  OP_POP,
  OP_GET_GLOBAL,
  OP_SET_GLOBAL,
  OP_TOPLA,
  OP_CIKAR,
  OP_CARP,
  OP_BOL,
  OP_NEGATE,
  OP_NOT,
  OP_ESIT,
  OP_BUYUK,
  OP_KUCUK,
  OP_VE,
  OP_VEYA,
  OP_YAZDIR,
  OP_ATLA,
  OP_ATLA_EGER_YANLIS,
  OP_DONGU,
  OP_DON
};

