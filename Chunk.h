#pragma once

#include "OpCode.h"

#include <cstddef>
#include <cstdint>
#include <string>
#include <variant>
#include <vector>

// VM icinde tasinan minimum deger tipi.
// Faz 1'de performans hedefi icin yalnizca temel tipleri aciyoruz.
struct VMValue {
  using Veri = std::variant<std::monostate, double, std::string, bool>;
  Veri veri{};

  VMValue() : veri(std::monostate{}) {}
  explicit VMValue(double v) : veri(v) {}
  explicit VMValue(bool v) : veri(v) {}
  explicit VMValue(std::string v) : veri(std::move(v)) {}
  explicit VMValue(const char* v) : veri(std::string(v)) {}
};

// Bytecode + satir bilgisi + sabit havuzu.
struct BytecodeChunk {
  std::vector<std::uint8_t> kod;
  std::vector<std::size_t> satirlar;
  std::vector<VMValue> sabitler;

  void yazByte(std::uint8_t byte, std::size_t satir);
  void yazOpCode(OpCode op, std::size_t satir);
  void yazU16(std::uint16_t deger, std::size_t satir);
  std::uint16_t sabitEkle(const VMValue& deger);
};

// Serilestirme yardimcilari:
// .obc dosyasi veya paketli .exe payloadi icin kullanilir.
std::vector<std::uint8_t> chunkSerilestir(const BytecodeChunk& chunk);
BytecodeChunk chunkCoz(const std::vector<std::uint8_t>& hamVeri);

