# Orhun Migration Guide (V2)

## 1. VM Fallback Davranışı
- Varsayılan davranış VM'dir.
- Fallback varsayılanı artık kanal bazlıdır:
  - `stable` -> kapalı
  - `beta/nightly/dev` -> açık
- Kanal seçimi:
  - `ORHUN_CHANNEL=stable|beta|nightly|dev`
  - (alternatif) `ORHUN_RELEASE_CHANNEL=...`
- Manuel override:
  - `ORHUN_VM_FALLBACK=0` -> fallback kapalı
  - `ORHUN_VM_FALLBACK=1` -> fallback açık

## 2. Güvenli Komut Çalıştırma
- `sistem.komut` artık varsayılan kısıtlı modda.
- Tehlikeli karakter içeren komutlar engellenir.
- Gerekirse açık mod:
  - `ORHUN_UNSAFE=1`
  - veya `ORHUN_SYSTEM_UNSAFE=1`

## 3. Paket Güveni
- Uzak kaynaklar allowlist ile doğrulanır.
- Ek izinli alan adları:
  - `ORHUN_PAKET_ALLOWLIST=example.com,git.example.org`
- Paket kurulumu `orhun.lock` günceller.

## 4. Derleme Metadata
- `orhun derle` artık:
  - `.obc`
  - `.exe`
  - `.obc.meta.json` üretir
- `.obc.meta.json` dosyasında payload boyutu ve CRC32 bulunur.

## 5. Benchmark Semantiği (`orhun hiz`)
- Yeni ölçüm seçenekleri:
  - `--olcum-modu=runtime|full` (varsayılan: `runtime`)
  - `--warmup=N` (varsayılan: `10`)
- `runtime` modu:
  - Parse + VM compile bir kez yapılır.
  - Tekrar döngüsünde sadece çalışma süresi ölçülür.
- `full` modu:
  - Parse + compile + run toplam maliyeti ölçülür.
- `--json` çıktısında yeni alanlar:
  - `olcum_modu`
  - `warmup`
  - `parse_ms`
  - `vm_compile_ms`
  - `gate_result`

## 6. Benchmark Gate Modu
- `tests/benchmark_gate.ps1` ve `tests/benchmark_gate.sh` iki mod destekler:
  - `suite` (varsayılan): tüm test seti için medyan P50/P90 üzerinden kapı.
  - `per_case`: her test dosyası için tek tek kapı.
- Önerilen CI kullanımı:
  - nightly/beta için `suite` + aşamalı eşikler
  - stabil sürüm adayı için `per_case` + daha sıkı eşikler
