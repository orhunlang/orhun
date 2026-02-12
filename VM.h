#pragma once

#include "Chunk.h"

#include <cstddef>
#include <string>
#include <unordered_map>
#include <vector>

// Stack tabanli bytecode sanal makinesi.
class VM {
public:
  void sifirla();
  void calistir(const BytecodeChunk& chunk);

private:
  const BytecodeChunk* chunk_ = nullptr;
  std::size_t ip_ = 0;
  std::vector<VMValue> yigin_;
  std::unordered_map<std::string, VMValue> globaller_;

  void yiginPush(VMValue deger);
  VMValue yiginPop();
  const VMValue& yiginBak(std::size_t tersten) const;

  std::uint8_t byteOku();
  std::uint16_t u16Oku();
  const VMValue& sabitOku(std::uint16_t indeks) const;

  bool falseMi(const VMValue& deger) const;
  bool esitMi(const VMValue& sol, const VMValue& sag) const;
  std::string metneCevir(const VMValue& deger) const;
  double sayiyaCevir(const VMValue& deger, const std::string& baglam) const;

  [[noreturn]] void calismaHatasi(const std::string& mesaj) const;
};

