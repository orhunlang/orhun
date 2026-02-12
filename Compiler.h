#pragma once

#include "AST.h"
#include "Chunk.h"

#include <cstddef>
#include <string>

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

  void opcodeYaz(OpCode op, std::size_t satir);
  void sabitYaz(const VMValue& deger, std::size_t satir);
  void globalOperandYaz(OpCode op, const std::string& ad, std::size_t satir);
  std::size_t atlaYaz(OpCode op, std::size_t satir);
  void atlaYamala(std::size_t ofsetIndeksi);
  void donguYaz(std::size_t loopBaslangic, std::size_t satir);

  [[noreturn]] void derlemeHatasi(std::size_t satir, const std::string& mesaj);
};

