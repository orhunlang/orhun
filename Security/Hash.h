#pragma once

#include <array>
#include <cstdint>
#include <iomanip>
#include <sstream>
#include <string>
#include <vector>

namespace security {

namespace detail {

inline std::uint32_t rotr(std::uint32_t x, std::uint32_t n) {
  return (x >> n) | (x << (32u - n));
}

inline std::array<std::uint32_t, 64> kSabitleri() {
  return {
      0x428a2f98u, 0x71374491u, 0xb5c0fbcfu, 0xe9b5dba5u, 0x3956c25bu,
      0x59f111f1u, 0x923f82a4u, 0xab1c5ed5u, 0xd807aa98u, 0x12835b01u,
      0x243185beu, 0x550c7dc3u, 0x72be5d74u, 0x80deb1feu, 0x9bdc06a7u,
      0xc19bf174u, 0xe49b69c1u, 0xefbe4786u, 0x0fc19dc6u, 0x240ca1ccu,
      0x2de92c6fu, 0x4a7484aau, 0x5cb0a9dcu, 0x76f988dau, 0x983e5152u,
      0xa831c66du, 0xb00327c8u, 0xbf597fc7u, 0xc6e00bf3u, 0xd5a79147u,
      0x06ca6351u, 0x14292967u, 0x27b70a85u, 0x2e1b2138u, 0x4d2c6dfcu,
      0x53380d13u, 0x650a7354u, 0x766a0abbu, 0x81c2c92eu, 0x92722c85u,
      0xa2bfe8a1u, 0xa81a664bu, 0xc24b8b70u, 0xc76c51a3u, 0xd192e819u,
      0xd6990624u, 0xf40e3585u, 0x106aa070u, 0x19a4c116u, 0x1e376c08u,
      0x2748774cu, 0x34b0bcb5u, 0x391c0cb3u, 0x4ed8aa4au, 0x5b9cca4fu,
      0x682e6ff3u, 0x748f82eeu, 0x78a5636fu, 0x84c87814u, 0x8cc70208u,
      0x90befffau, 0xa4506cebu, 0xbef9a3f7u, 0xc67178f2u};
}

}  // namespace detail

inline std::string sha256Hex(const std::vector<std::uint8_t>& girdi) {
  std::vector<std::uint8_t> veri = girdi;
  const std::uint64_t bitUzunlugu = static_cast<std::uint64_t>(veri.size()) * 8ull;

  veri.push_back(0x80u);
  while ((veri.size() % 64u) != 56u) {
    veri.push_back(0x00u);
  }
  for (int i = 7; i >= 0; --i) {
    veri.push_back(static_cast<std::uint8_t>((bitUzunlugu >> (i * 8)) & 0xFFu));
  }

  std::uint32_t h0 = 0x6a09e667u;
  std::uint32_t h1 = 0xbb67ae85u;
  std::uint32_t h2 = 0x3c6ef372u;
  std::uint32_t h3 = 0xa54ff53au;
  std::uint32_t h4 = 0x510e527fu;
  std::uint32_t h5 = 0x9b05688cu;
  std::uint32_t h6 = 0x1f83d9abu;
  std::uint32_t h7 = 0x5be0cd19u;
  const auto k = detail::kSabitleri();

  std::array<std::uint32_t, 64> w{};
  for (std::size_t ofset = 0; ofset < veri.size(); ofset += 64u) {
    for (int i = 0; i < 16; ++i) {
      const std::size_t idx = ofset + static_cast<std::size_t>(i) * 4u;
      w[static_cast<std::size_t>(i)] =
          (static_cast<std::uint32_t>(veri[idx]) << 24u) |
          (static_cast<std::uint32_t>(veri[idx + 1]) << 16u) |
          (static_cast<std::uint32_t>(veri[idx + 2]) << 8u) |
          static_cast<std::uint32_t>(veri[idx + 3]);
    }
    for (int i = 16; i < 64; ++i) {
      const std::uint32_t s0 =
          detail::rotr(w[static_cast<std::size_t>(i - 15)], 7u) ^
          detail::rotr(w[static_cast<std::size_t>(i - 15)], 18u) ^
          (w[static_cast<std::size_t>(i - 15)] >> 3u);
      const std::uint32_t s1 =
          detail::rotr(w[static_cast<std::size_t>(i - 2)], 17u) ^
          detail::rotr(w[static_cast<std::size_t>(i - 2)], 19u) ^
          (w[static_cast<std::size_t>(i - 2)] >> 10u);
      w[static_cast<std::size_t>(i)] =
          w[static_cast<std::size_t>(i - 16)] + s0 +
          w[static_cast<std::size_t>(i - 7)] + s1;
    }

    std::uint32_t a = h0;
    std::uint32_t b = h1;
    std::uint32_t c = h2;
    std::uint32_t d = h3;
    std::uint32_t e = h4;
    std::uint32_t f = h5;
    std::uint32_t g = h6;
    std::uint32_t h = h7;

    for (int i = 0; i < 64; ++i) {
      const std::uint32_t s1 =
          detail::rotr(e, 6u) ^ detail::rotr(e, 11u) ^ detail::rotr(e, 25u);
      const std::uint32_t ch = (e & f) ^ ((~e) & g);
      const std::uint32_t temp1 =
          h + s1 + ch + k[static_cast<std::size_t>(i)] + w[static_cast<std::size_t>(i)];
      const std::uint32_t s0 =
          detail::rotr(a, 2u) ^ detail::rotr(a, 13u) ^ detail::rotr(a, 22u);
      const std::uint32_t maj = (a & b) ^ (a & c) ^ (b & c);
      const std::uint32_t temp2 = s0 + maj;

      h = g;
      g = f;
      f = e;
      e = d + temp1;
      d = c;
      c = b;
      b = a;
      a = temp1 + temp2;
    }

    h0 += a;
    h1 += b;
    h2 += c;
    h3 += d;
    h4 += e;
    h5 += f;
    h6 += g;
    h7 += h;
  }

  std::ostringstream ss;
  ss << std::hex << std::setfill('0') << std::nouppercase;
  const std::array<std::uint32_t, 8> sonuc = {h0, h1, h2, h3, h4, h5, h6, h7};
  for (std::uint32_t h : sonuc) {
    ss << std::setw(8) << h;
  }
  return ss.str();
}

inline std::string sha256Hex(const std::string& girdi) {
  return sha256Hex(std::vector<std::uint8_t>(girdi.begin(), girdi.end()));
}

}  // namespace security
