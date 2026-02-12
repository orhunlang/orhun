#include "Compiler.h"

#include <cstdlib>
#include <limits>
#include <stdexcept>

namespace {

bool opEsitMi(const std::string& sol, const char* sag) {
  return sol == sag;
}

}  // namespace

BytecodeChunk Compiler::derle(const ProgramNode* program) {
  if (program == nullptr) {
    throw std::runtime_error("Derleyiciye bos program verildi.");
  }

  chunk_ = BytecodeChunk{};
  for (const auto& komut : program->komutlar()) {
    komutDerle(komut.get());
  }

  opcodeYaz(OpCode::OP_DON, program->satir());
  return chunk_;
}

void Compiler::komutDerle(const ASTNode* dugum) {
  if (dugum == nullptr) {
    return;
  }

  if (const auto* atama = dynamic_cast<const AtamaNode*>(dugum)) {
    atamaDerle(atama);
    return;
  }
  if (const auto* yazdir = dynamic_cast<const YazdirNode*>(dugum)) {
    yazdirDerle(yazdir);
    return;
  }
  if (const auto* eger = dynamic_cast<const EgerNode*>(dugum)) {
    egerDerle(eger);
    return;
  }
  if (const auto* surece = dynamic_cast<const SureceNode*>(dugum)) {
    sureceDerle(surece);
    return;
  }
  if (const auto* blok = dynamic_cast<const BlockNode*>(dugum)) {
    blokDerle(blok);
    return;
  }
  if (const auto* ifadeKomut = dynamic_cast<const IfadeKomutNode*>(dugum)) {
    ifadeKomutDerle(ifadeKomut);
    return;
  }

  derlemeHatasi(dugum->satir(),
                "Bu komut VM derleyicisinin Faz 1 kapsaminda degil.");
}

void Compiler::blokDerle(const BlockNode* dugum) {
  if (dugum == nullptr) {
    return;
  }
  for (const auto& komut : dugum->komutlar()) {
    komutDerle(komut.get());
  }
}

void Compiler::ifadeDerle(const ASTNode* dugum) {
  if (dugum == nullptr) {
    derlemeHatasi(0, "Bos ifade derlenemiyor.");
  }

  if (const auto* sayi = dynamic_cast<const SayiNode*>(dugum)) {
    char* bitis = nullptr;
    const double deger = std::strtod(sayi->deger().c_str(), &bitis);
    if (bitis == sayi->deger().c_str() || (bitis != nullptr && *bitis != '\0')) {
      derlemeHatasi(sayi->satir(),
                    "Sayi sabiti parse edilemedi: '" + sayi->deger() + "'.");
    }
    sabitYaz(VMValue(deger), sayi->satir());
    return;
  }

  if (const auto* metin = dynamic_cast<const MetinNode*>(dugum)) {
    sabitYaz(VMValue(metin->deger()), metin->satir());
    return;
  }

  if (const auto* mantik = dynamic_cast<const MantikNode*>(dugum)) {
    opcodeYaz(mantik->deger() ? OpCode::OP_DOGRU : OpCode::OP_YANLIS,
              mantik->satir());
    return;
  }

  if (const auto* kimlik = dynamic_cast<const KimlikNode*>(dugum)) {
    globalOperandYaz(OpCode::OP_GET_GLOBAL, kimlik->ad(), kimlik->satir());
    return;
  }

  if (const auto* tekli = dynamic_cast<const TekliIslemNode*>(dugum)) {
    ifadeDerle(tekli->ifade());
    if (opEsitMi(tekli->op(), "-")) {
      opcodeYaz(OpCode::OP_NEGATE, tekli->satir());
      return;
    }
    if (opEsitMi(tekli->op(), "değil") || opEsitMi(tekli->op(), "degil")) {
      opcodeYaz(OpCode::OP_NOT, tekli->satir());
      return;
    }
    derlemeHatasi(tekli->satir(),
                  "Desteklenmeyen tekli operator: '" + tekli->op() + "'.");
  }

  if (const auto* ikili = dynamic_cast<const IkiliIslemNode*>(dugum)) {
    ifadeDerle(ikili->sol());
    ifadeDerle(ikili->sag());

    const std::string& op = ikili->op();
    if (opEsitMi(op, "+")) {
      opcodeYaz(OpCode::OP_TOPLA, ikili->satir());
      return;
    }
    if (opEsitMi(op, "-")) {
      opcodeYaz(OpCode::OP_CIKAR, ikili->satir());
      return;
    }
    if (opEsitMi(op, "*")) {
      opcodeYaz(OpCode::OP_CARP, ikili->satir());
      return;
    }
    if (opEsitMi(op, "/")) {
      opcodeYaz(OpCode::OP_BOL, ikili->satir());
      return;
    }
    if (opEsitMi(op, "eşit") || opEsitMi(op, "esit") || opEsitMi(op, "==")) {
      opcodeYaz(OpCode::OP_ESIT, ikili->satir());
      return;
    }
    if (opEsitMi(op, "eşit_değil") || opEsitMi(op, "esit_degil") ||
        opEsitMi(op, "!=")) {
      opcodeYaz(OpCode::OP_ESIT, ikili->satir());
      opcodeYaz(OpCode::OP_NOT, ikili->satir());
      return;
    }
    if (opEsitMi(op, "büyük") || opEsitMi(op, "buyuk") || opEsitMi(op, ">")) {
      opcodeYaz(OpCode::OP_BUYUK, ikili->satir());
      return;
    }
    if (opEsitMi(op, "küçük") || opEsitMi(op, "kucuk") || opEsitMi(op, "<")) {
      opcodeYaz(OpCode::OP_KUCUK, ikili->satir());
      return;
    }
    if (opEsitMi(op, ">=")) {
      opcodeYaz(OpCode::OP_KUCUK, ikili->satir());
      opcodeYaz(OpCode::OP_NOT, ikili->satir());
      return;
    }
    if (opEsitMi(op, "<=")) {
      opcodeYaz(OpCode::OP_BUYUK, ikili->satir());
      opcodeYaz(OpCode::OP_NOT, ikili->satir());
      return;
    }
    if (opEsitMi(op, "ve")) {
      opcodeYaz(OpCode::OP_VE, ikili->satir());
      return;
    }
    if (opEsitMi(op, "veya")) {
      opcodeYaz(OpCode::OP_VEYA, ikili->satir());
      return;
    }

    derlemeHatasi(ikili->satir(),
                  "Desteklenmeyen ikili operator: '" + ikili->op() + "'.");
  }

  derlemeHatasi(dugum->satir(),
                "Bu ifade VM derleyicisinin Faz 1 kapsaminda degil.");
}

void Compiler::atamaDerle(const AtamaNode* dugum) {
  const auto* kimlik = dynamic_cast<const KimlikNode*>(dugum->hedef());
  if (kimlik == nullptr) {
    derlemeHatasi(dugum->satir(),
                  "VM Faz 1 su an sadece degisken atamasini destekliyor.");
  }

  ifadeDerle(dugum->ifade());
  globalOperandYaz(OpCode::OP_SET_GLOBAL, kimlik->ad(), dugum->satir());
  opcodeYaz(OpCode::OP_POP, dugum->satir());
}

void Compiler::yazdirDerle(const YazdirNode* dugum) {
  ifadeDerle(dugum->ifade());
  opcodeYaz(OpCode::OP_YAZDIR, dugum->satir());
}

void Compiler::egerDerle(const EgerNode* dugum) {
  ifadeDerle(dugum->kosul());
  const std::size_t yanlisaAtla = atlaYaz(OpCode::OP_ATLA_EGER_YANLIS, dugum->satir());
  opcodeYaz(OpCode::OP_POP, dugum->satir());
  blokDerle(dugum->dogruBlok());

  if (dugum->yanlisBlok() != nullptr) {
    const std::size_t sonaAtla = atlaYaz(OpCode::OP_ATLA, dugum->satir());
    atlaYamala(yanlisaAtla);
    opcodeYaz(OpCode::OP_POP, dugum->satir());
    blokDerle(dugum->yanlisBlok());
    atlaYamala(sonaAtla);
    return;
  }

  atlaYamala(yanlisaAtla);
  opcodeYaz(OpCode::OP_POP, dugum->satir());
}

void Compiler::sureceDerle(const SureceNode* dugum) {
  const std::size_t loopBaslangic = chunk_.kod.size();

  ifadeDerle(dugum->kosul());
  const std::size_t cikisAtlamasi =
      atlaYaz(OpCode::OP_ATLA_EGER_YANLIS, dugum->satir());
  opcodeYaz(OpCode::OP_POP, dugum->satir());

  blokDerle(dugum->govde());
  donguYaz(loopBaslangic, dugum->satir());

  atlaYamala(cikisAtlamasi);
  opcodeYaz(OpCode::OP_POP, dugum->satir());
}

void Compiler::ifadeKomutDerle(const IfadeKomutNode* dugum) {
  ifadeDerle(dugum->ifade());
  opcodeYaz(OpCode::OP_POP, dugum->satir());
}

void Compiler::opcodeYaz(OpCode op, std::size_t satir) {
  chunk_.yazOpCode(op, satir);
}

void Compiler::sabitYaz(const VMValue& deger, std::size_t satir) {
  const std::uint16_t sabitIndeksi = chunk_.sabitEkle(deger);
  chunk_.yazOpCode(OpCode::OP_SABIT, satir);
  chunk_.yazU16(sabitIndeksi, satir);
}

void Compiler::globalOperandYaz(OpCode op, const std::string& ad,
                                std::size_t satir) {
  const std::uint16_t sabitIndeksi = chunk_.sabitEkle(VMValue(ad));
  chunk_.yazOpCode(op, satir);
  chunk_.yazU16(sabitIndeksi, satir);
}

std::size_t Compiler::atlaYaz(OpCode op, std::size_t satir) {
  chunk_.yazOpCode(op, satir);
  chunk_.yazByte(0xFF, satir);
  chunk_.yazByte(0xFF, satir);
  return chunk_.kod.size() - 2;
}

void Compiler::atlaYamala(std::size_t ofsetIndeksi) {
  if (ofsetIndeksi + 1 >= chunk_.kod.size()) {
    throw std::runtime_error("Ic hata: yamalanacak atlama ofseti gecersiz.");
  }

  const std::size_t gecisMesafesi = chunk_.kod.size() - ofsetIndeksi - 2;
  if (gecisMesafesi > std::numeric_limits<std::uint16_t>::max()) {
    throw std::runtime_error("Derleme hatasi: atlama mesafesi cok buyuk.");
  }

  chunk_.kod[ofsetIndeksi] =
      static_cast<std::uint8_t>((gecisMesafesi >> 8) & 0xFF);
  chunk_.kod[ofsetIndeksi + 1] =
      static_cast<std::uint8_t>(gecisMesafesi & 0xFF);
}

void Compiler::donguYaz(std::size_t loopBaslangic, std::size_t satir) {
  const std::size_t komutBaslangici = chunk_.kod.size();
  chunk_.yazOpCode(OpCode::OP_DONGU, satir);

  const std::size_t ofset = komutBaslangici + 3 - loopBaslangic;
  if (ofset > std::numeric_limits<std::uint16_t>::max()) {
    throw std::runtime_error("Derleme hatasi: dongu geri atlamasi cok buyuk.");
  }
  chunk_.yazU16(static_cast<std::uint16_t>(ofset), satir);
}

[[noreturn]] void Compiler::derlemeHatasi(std::size_t satir,
                                          const std::string& mesaj) {
  throw std::runtime_error("VM Derleme Hatasi (satir " +
                           std::to_string(satir) + "): " + mesaj);
}

