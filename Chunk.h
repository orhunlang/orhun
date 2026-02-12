#pragma once

#include "OpCode.h"
#include "Value.h"

#include <cstddef>
#include <cstdint>
#include <string>
#include <variant>
#include <vector>

// Bytecode sabit havuzu compile-time veri tasir.
// Runtime Value'dan farkli olarak metin burada ham std::string olarak saklanir.
struct SabitDeger {
  using Veri = std::variant<std::monostate, double, std::string, bool>;
  Veri veri{};

  SabitDeger() : veri(std::monostate{}) {}
  explicit SabitDeger(double v) : veri(v) {}
  explicit SabitDeger(bool v) : veri(v) {}
  explicit SabitDeger(std::string v) : veri(std::move(v)) {}
  explicit SabitDeger(const char* v) : veri(std::string(v)) {}
};

struct BytecodeChunk {
  std::vector<std::uint8_t> kod;
  std::vector<std::size_t> satirlar;
  std::vector<SabitDeger> sabitler;

  void yazByte(std::uint8_t byte, std::size_t satir);
  void yazOpCode(OpCode op, std::size_t satir);
  void yazU16(std::uint16_t deger, std::size_t satir);
  std::uint16_t sabitEkle(const SabitDeger& deger);
};

std::vector<std::uint8_t> chunkSerilestir(const BytecodeChunk& chunk);
BytecodeChunk chunkCoz(const std::vector<std::uint8_t>& hamVeri);
