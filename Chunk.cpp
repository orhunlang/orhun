#include "Chunk.h"

#include <algorithm>
#include <cstring>
#include <limits>
#include <stdexcept>

namespace {

constexpr std::uint8_t kSihir[4] = {'O', 'B', 'C', '1'};

void yazU32(std::vector<std::uint8_t>& hedef, std::uint32_t deger) {
  hedef.push_back(static_cast<std::uint8_t>(deger & 0xFF));
  hedef.push_back(static_cast<std::uint8_t>((deger >> 8) & 0xFF));
  hedef.push_back(static_cast<std::uint8_t>((deger >> 16) & 0xFF));
  hedef.push_back(static_cast<std::uint8_t>((deger >> 24) & 0xFF));
}

std::uint32_t okuU32(const std::vector<std::uint8_t>& veri, std::size_t& ofset) {
  if (ofset + 4 > veri.size()) {
    throw std::runtime_error("Bozuk bytecode: U32 okunamadi.");
  }

  std::uint32_t sonuc = 0;
  sonuc |= static_cast<std::uint32_t>(veri[ofset]);
  sonuc |= static_cast<std::uint32_t>(veri[ofset + 1]) << 8;
  sonuc |= static_cast<std::uint32_t>(veri[ofset + 2]) << 16;
  sonuc |= static_cast<std::uint32_t>(veri[ofset + 3]) << 24;
  ofset += 4;
  return sonuc;
}

void byteDizisiniYaz(std::vector<std::uint8_t>& hedef, const void* kaynak,
                     std::size_t boyut) {
  const auto* ham = static_cast<const std::uint8_t*>(kaynak);
  hedef.insert(hedef.end(), ham, ham + boyut);
}

}  // namespace

void BytecodeChunk::yazByte(std::uint8_t byte, std::size_t satir) {
  kod.push_back(byte);
  satirlar.push_back(satir);
}

void BytecodeChunk::yazOpCode(OpCode op, std::size_t satir) {
  yazByte(static_cast<std::uint8_t>(op), satir);
}

void BytecodeChunk::yazU16(std::uint16_t deger, std::size_t satir) {
  yazByte(static_cast<std::uint8_t>((deger >> 8) & 0xFF), satir);
  yazByte(static_cast<std::uint8_t>(deger & 0xFF), satir);
}

std::uint16_t BytecodeChunk::sabitEkle(const SabitDeger& deger) {
  if (sabitler.size() >= std::numeric_limits<std::uint16_t>::max()) {
    throw std::runtime_error("Sabit havuzu limiti asildi (65535).");
  }
  sabitler.push_back(deger);
  return static_cast<std::uint16_t>(sabitler.size() - 1);
}

std::vector<std::uint8_t> chunkSerilestir(const BytecodeChunk& chunk) {
  std::vector<std::uint8_t> ham;
  ham.reserve(64 + chunk.kod.size());

  ham.insert(ham.end(), std::begin(kSihir), std::end(kSihir));

  yazU32(ham, static_cast<std::uint32_t>(chunk.sabitler.size()));
  for (const SabitDeger& deger : chunk.sabitler) {
    if (std::holds_alternative<std::monostate>(deger.veri)) {
      ham.push_back(0);
      continue;
    }
    if (const auto* sayi = std::get_if<double>(&deger.veri)) {
      ham.push_back(1);
      byteDizisiniYaz(ham, sayi, sizeof(double));
      continue;
    }
    if (const auto* metin = std::get_if<std::string>(&deger.veri)) {
      ham.push_back(2);
      yazU32(ham, static_cast<std::uint32_t>(metin->size()));
      byteDizisiniYaz(ham, metin->data(), metin->size());
      continue;
    }
    if (const auto* mantik = std::get_if<bool>(&deger.veri)) {
      ham.push_back(3);
      ham.push_back(*mantik ? 1 : 0);
      continue;
    }
  }

  yazU32(ham, static_cast<std::uint32_t>(chunk.kod.size()));
  byteDizisiniYaz(ham, chunk.kod.data(), chunk.kod.size());

  yazU32(ham, static_cast<std::uint32_t>(chunk.satirlar.size()));
  for (std::size_t satir : chunk.satirlar) {
    yazU32(ham, static_cast<std::uint32_t>(satir));
  }

  return ham;
}

BytecodeChunk chunkCoz(const std::vector<std::uint8_t>& hamVeri) {
  if (hamVeri.size() < 4 ||
      !std::equal(std::begin(kSihir), std::end(kSihir), hamVeri.begin())) {
    throw std::runtime_error("Gecersiz bytecode: OBC sihir imzasi okunamadi.");
  }

  BytecodeChunk chunk;
  std::size_t ofset = 4;

  const std::uint32_t sabitSayisi = okuU32(hamVeri, ofset);
  chunk.sabitler.reserve(sabitSayisi);
  for (std::uint32_t i = 0; i < sabitSayisi; ++i) {
    if (ofset >= hamVeri.size()) {
      throw std::runtime_error("Bozuk bytecode: sabit tipi okunamadi.");
    }
    const std::uint8_t tip = hamVeri[ofset++];
    switch (tip) {
      case 0:
        chunk.sabitler.emplace_back();
        break;
      case 1: {
        if (ofset + sizeof(double) > hamVeri.size()) {
          throw std::runtime_error("Bozuk bytecode: sayi sabiti eksik.");
        }
        double sayi = 0.0;
        std::memcpy(&sayi, hamVeri.data() + ofset, sizeof(double));
        ofset += sizeof(double);
        chunk.sabitler.emplace_back(sayi);
        break;
      }
      case 2: {
        const std::uint32_t uzunluk = okuU32(hamVeri, ofset);
        if (ofset + uzunluk > hamVeri.size()) {
          throw std::runtime_error("Bozuk bytecode: metin sabiti eksik.");
        }
        std::string metin(
            reinterpret_cast<const char*>(hamVeri.data() + ofset), uzunluk);
        ofset += uzunluk;
        chunk.sabitler.emplace_back(std::move(metin));
        break;
      }
      case 3: {
        if (ofset >= hamVeri.size()) {
          throw std::runtime_error("Bozuk bytecode: mantik sabiti eksik.");
        }
        chunk.sabitler.emplace_back(hamVeri[ofset++] != 0);
        break;
      }
      default:
        throw std::runtime_error("Bozuk bytecode: bilinmeyen sabit tipi.");
    }
  }

  const std::uint32_t kodBoyutu = okuU32(hamVeri, ofset);
  if (ofset + kodBoyutu > hamVeri.size()) {
    throw std::runtime_error("Bozuk bytecode: kod bolgesi eksik.");
  }
  chunk.kod.assign(hamVeri.begin() + static_cast<std::ptrdiff_t>(ofset),
                   hamVeri.begin() +
                       static_cast<std::ptrdiff_t>(ofset + kodBoyutu));
  ofset += kodBoyutu;

  const std::uint32_t satirBoyutu = okuU32(hamVeri, ofset);
  chunk.satirlar.reserve(satirBoyutu);
  for (std::uint32_t i = 0; i < satirBoyutu; ++i) {
    chunk.satirlar.push_back(okuU32(hamVeri, ofset));
  }

  if (chunk.satirlar.size() != chunk.kod.size()) {
    throw std::runtime_error("Bozuk bytecode: satir/kod boyutu uyusmuyor.");
  }

  if (ofset != hamVeri.size()) {
    throw std::runtime_error("Bozuk bytecode: dosya sonu beklendiginden farkli.");
  }

  return chunk;
}
