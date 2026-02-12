#pragma once

#include "AST.h"
#include "Chunk.h"

#include <cstddef>
#include <string>
#include <unordered_map>

// AST -> Bytecode derleyicisi (Faz 1).
// Bilerek kademeli: cekirdek komutlari optimize eder, geri kalan dugumleri
// acik bir hata ile raporlar.
class Compiler {
public:
  BytecodeChunk derle(const ProgramNode* program);

private:
  BytecodeChunk chunk_;

  void komutDerle(const ASTNode* dugum);
  void blokDerle(const BlockNode* dugum);
  void ifadeDerle(const ASTNode* dugum);

  void atamaDerle(const AtamaNode* dugum);
  void yazdirDerle(const YazdirNode* dugum);
  void egerDerle(const EgerNode* dugum);
  void sureceDerle(const SureceNode* dugum);
  void ifadeKomutDerle(const IfadeKomutNode* dugum);
  void cagrilanAdYukle(const std::string& ad, std::size_t satir);
  void islevTanimDerle(const IslevTanimNode* dugum);
  void sinifTanimDerle(const SinifTanimNode* dugum);
  void dondurDerle(const DondurNode* dugum);
  void islevLiteralDerle(const IslevTanimNode* dugum, bool metodMu,
                         bool ustGerekiyor, const std::string& kayitAdi,
                         const std::string& sinifAdi);
  std::uint16_t localAlVeyaOlustur(const std::string& ad);
  const std::uint16_t* localBul(const std::string& ad) const;
  bool islevIcindeyim() const;

  void opcodeYaz(OpCode op, std::size_t satir);
  void sabitYaz(const SabitDeger& deger, std::size_t satir);
  void globalOperandYaz(OpCode op, const std::string& ad, std::size_t satir);
  std::size_t atlaYaz(OpCode op, std::size_t satir);
  void atlaYamala(std::size_t ofsetIndeksi);
  void donguYaz(std::size_t loopBaslangic, std::size_t satir);

  [[noreturn]] void derlemeHatasi(std::size_t satir, const std::string& mesaj);

  struct IslevBaglami {
    bool metodMu = false;
    std::unordered_map<std::string, std::uint16_t> localIndeksler;
    std::uint16_t sonrakiLocal = 0;
  };
  std::vector<IslevBaglami> islevYigini_;
};
