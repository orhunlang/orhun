# Orhun Ilk 3 Yol Haritasi (2026 -> 2029)

Bu belge, mevcut kod tabaninin gercek durumuna gore "genel amacli dunyada ilk 3" hedefi icin teknik ve urun yol haritasini tanimlar.

## Durum (17 Subat 2026)

- Baslatildi: Faz 1A `?.` guvenli erisim MVP (lexer + parser + AST + compiler +
  VM + test)
- Baslatildi: Faz 1B hata-degeri modeli MVP
  (`sonuc.ok(...)` / `sonuc.hata(...)` + test)
- Baslatildi: Faz 1C Turkce-kati modu MVP
  (`--turkce-kati` / `ORHUN_TURKCE_KATI=1`, `dis_islev` alias devre disi)
- Baslatildi: Faz 2A `paralel yap:` MVP v2
  (v2: cok komutlu blok -> `gorev.baslat_plan(...)` adim modeli)

## 1) Mevcut Durum (Kod Analizi Ozeti)

- Orhun VM tabanli bytecode calistiriyor:
  - `main.cpp:2056` -> AST -> bytecode derleme
  - `VM.cpp:2048` -> bytecode yurutme dongusu
  - `main.cpp:2198` -> `derle` komutu (`.obc` + paketli `.exe`)
- GC var ve otomatik:
  - `Memory.h:10` -> stop-the-world mark-sweep
  - `VM.cpp:1970` -> root set isaretleme
- Eszamanlilik altyapisi var ve dil seviyesi MVP basladi:
  - `VM.cpp:1125` -> `gorev.*` modulu (`baslat_bekle`, `bekle`, `hepsi_bekle`)
  - `paralel yap:` sentaksi var (MVP v2, cok komutlu blokta `bekle(...)` /
    `sistem.komut(...)` adimlari)
- Hata yakalama var:
  - `Parser.cpp:430` -> `deneme/yakala`
  - `Compiler.cpp:1079` -> TRY opcode uretimi
- Hata-degeri modeli MVP var:
  - `sonuc.ok(...)` / `sonuc.hata(...)` stdlib modulu
- Turkce-kati modu MVP var:
  - `--turkce-kati` / `ORHUN_TURKCE_KATI=1` ile ASCII alias kilidi
- Guvenli erisim operatoru var:
  - `?.` lexer + parser + AST + compiler + VM yolunda destekli
- Sunucu var ama statik dosya sunumu odakli:
  - `VM.cpp:1074` -> `sunucu.baslat/durdur/calisiyor_mu`
  - `StdLib/Sunucu.h` -> GET + statik dosya sunucu, route/callback yok
- Performans disiplini ve CI guclu:
  - `.github/workflows/ci.yml` -> cross-platform test, parity, fuzz, benchmark, LSP
  - `main.cpp:2039` -> `hiz` komutu (runtime/full olcum)
- VM fallback mekanizmasi hala mevcut:
  - `main.cpp:1836` -> `ORH-COMP-*` hatalarinda yorumlayici fallback

## 2) Hedef Tanimi ve KPI

Ilk 3 hedefi tek metrikle olmaz. Asagidaki 4 eksende ayni anda ilerleme zorunlu:

1. Performans
2. Kolaylik (DX)
3. Ekosistem
4. Guvenilirlik

Olculebilir KPI seti:

- Performans KPI-1: `tests/benchmark_python_gate.py` medyan `p50 >= 1.05x` (6 ay), `>= 1.30x` (18 ay), `>= 1.70x` (36 ay)
- Performans KPI-2: "yavas vaka" sayisi (Python'dan yavas bench) 6'dan 2'nin altina inmeli
- Guvenilirlik KPI-1: stable kanalda fallback kullanimi %0 (VM strict parity)
- Guvenilirlik KPI-2: coverage gate min line coverage `%55 -> %70 -> %80`
- DX KPI-1: "ilk calisan uygulama" suresi 60 dk altina indirilmeli
- Ekosistem KPI-1: resmi paket sayisi, indirilen paket sayisi, aktif topluluk katkisi
- Ekosistem KPI-2: LSP kullanan proje sayisi, VSCode eklenti kurulum sayisi

## 3) Stratejik Konumlandirma

Kisa vadede "dunyada genel amacli ilk 3" teknik olarak gercekci degil.
Dogru sira:

1. Turkiye'de "egitim + hizli prototipleme" kategorisinde 1 numara
2. Bolgesel ve niche dominasyon (Turkce-first developer experience)
3. Buradan global genel amacli rekabete cikis

Dil kimligi korunacak:

- Anahtar kelimeler Turkce kalacak
- Hata mesajlari Turkce kalacak
- Turkce karakter destegi korunacak

## 4) Faz Bazli Yol Haritasi

## Faz 0 (0-6 hafta): Olcum ve Teknik Borc Temizligi

Teslimatlar:

- Tek benchmark kaynagi: `build/python_compare.json` otomatik uretim
- Mevcut `benchmarks_new.json` / `benchmarks_optimized.json` uyumsuzluklarini temizleme
- Fallback kaynakli `ORH-COMP-*` hatalarini kategori bazli raporlama
- Perf regression dashboard (JSON + markdown ozet)

Dosya odagi:

- `tests/benchmark_python_compare.py`
- `tests/benchmark_python_gate.py`
- `main.cpp` (`hiz` komutu)
- `docs/STATE_SNAPSHOT_*.md`

Basari kriteri:

- Her CI calismasinda tutarli benchmark artefakti
- Performans kararlarini tek veri setinden alabilme

## Faz 1 (1-4 ay): Dil Kolayligi ve Guvenlik Sicramasi

### 1A) Guvenli erisim `?.`

Hedef:

- `kullanici?.ad` ifadesi, `kullanici bos ise bos donsun` semantigi

Teknik:

- Lexer: `?` operator token destegi (`Lexer.cpp`)
- Parser: postfix zincire `?.` kolu (`Parser.cpp`)
- AST: guvenli alan erisimi dugumu (`AST.h`)
- Compiler/VM: null-guard opcode veya mevcut opcode kombinasyonu
- Test: `tests/cases/vm_safe_access.oh` + expected

### 1B) Hata degeri modeli (Rust/Kotlin ilhami)

Hedef:

- Sadece `deneme/yakala` degil, hata-deger akisi da olsun

Teknik:

- `sonuc.ok(...)` / `sonuc.hata(...)` stdlib ve pattern
- ileride dil seviyesinde sugar (faz 2)

Dosya odagi:

- `VM.cpp` (yerlesikler)
- `tests/cases/stdlib_sonuc.oh`

### 1C) Turkce-kati mod

Hedef:

- "tam Turkce dil" isteyenler icin kati calisma modu

Teknik:

- ASCII alias anahtar kelimeleri (ornek: `dis_islev`) opsiyonel engelle
- CLI bayragi veya env: `--turkce-kati` / `ORHUN_TURKCE_KATI=1`

Dosya odagi:

- `Lexer.cpp`, `Parser.cpp`, `main.cpp`

## Faz 2 (3-8 ay): Eszamanlilik ve Sunucu DX

### 2A) `paralel yap:` sozdizimi

Hedef:

- Kullanici API degil dil yapisi ile gorv baslatsin

Ornek:

```orhun
paralel yap:
    internet.indir("https://...", "veri.json")
```

Teknik:

- Yeni anahtar kelimeler: `paralel`, `yap`
- AST dugumu: `ParalelBlokNode`
- Compiler: bloktan closure/function uret, `gorev.baslat_*` benzeri primitive'e bagla
- VM: gorev kimligi + bekleme ergonomisi

Dosya odagi:

- `Lexer.cpp`
- `Parser.cpp`
- `AST.h`
- `Compiler.cpp`
- `VM.cpp`
- `tests/cases/stdlib_async.oh` genisletme

### 2B) Sunucu route API (JS/TS ilhami)

Hedef:

- `sunucu.dinle "/yol", islev(istek): ...` benzeri route tabanli API

Teknik:

- `StdLib/Sunucu.h` statik dosya sunumundan route tabanli isleme gecis
- HTTP method + path + body modelinin VM `Value` tipine map edilmesi

## Faz 3 (6-14 ay): VM Performans Cekirdegi

Hedef:

- VM'i Python seviyesinin ustune cikan bir varsayilan motor yapmak

Teslimatlar:

- Inline cache / polymorphic inline cache (global + alan + metod)
- Daha agresif peephole ve sabit katlama
- Siklikla kullanilan yerlesikler icin fast-path
- String birlestirme optimizasyonu (rope/builder stratejisi)
- Liste/sozluk allocation azaltimi

Dosya odagi:

- `Compiler.cpp` (`peepholeOptimize`, sabit katlama)
- `VM.cpp` (dispatch hot path, call path, allocations)
- `Value.h`, `Obj.h` (temsil optimizasyonlari)

Basari kriteri:

- Python compare medyan p50 >= 1.30x
- Yavas kalan benchmark sayisi <= 3

## Faz 4 (9-20 ay): GC 2.0 + JIT Hazirligi

### 4A) GC modernizasyonu

Mevcut:

- `Memory.h` mark-sweep ve duraklatmali

Hedef:

- Generational + incremental adimlarla duraklama azaltma

### 4B) Profil altyapisi

Hedef:

- Hangi opcode/trace "sicak" bilinmeden JIT yapilmamali

Teknik:

- opcode frekans sayaci
- call-site hotspot kayitlari

## Faz 5 (14-28 ay): JIT/AOT Cikti

Strateji:

1. Once AOT (C/LLVM IR veya dogrudan native backend)
2. Sonra hotspot JIT

Neden:

- Sifirdan JIT kurmak pahali; AOT ile once buyuk kazanc alinir

Opsiyonlar:

- AOT-C backend: bytecode -> C -> sistem derleyicisi
- LLVM backend: bytecode/IR -> makine kodu

Basari kriteri:

- AOT modunda C++/Rust sinifina yaklasan performans
- "VM default + AOT optional" urun modeli

## Faz 6 (18-30 ay): WASM ve Evrensellik

Hedef:

- Tarayicida calisan Orhun runtime

Teslimatlar:

- `orhun wasm derle dosya.oh`
- tarayici host API (dosya/network kisitli sandbox)
- Playground + paylasilabilir link

## Faz 7 (Paralel Surekli Is): Ekosistem ve Topluluk

Ilk 3 icin en kritik kaldirac budur.

Teslimatlar:

- Paket ekosistemi buyutme programi
- 100+ kaliteli ornek proje
- "1 saatte uygulama" egitim paketi
- Turkce ana dokuman + Ingilizce global dokuman
- VS Code eklentisi ve LSP iyilestirme dongusu

## 5) Ilk 8 Haftada Baslanacak Somut Isler

1. `?.` MVP
- Dosyalar: `Lexer.cpp`, `Parser.cpp`, `AST.h`, `Compiler.cpp`, `VM.cpp`
- Testler: `tests/cases/vm_safe_access.*`

2. `paralel yap:` MVP
- Dosyalar: `Lexer.cpp`, `Parser.cpp`, `AST.h`, `Compiler.cpp`, `VM.cpp`
- Testler: `tests/cases/stdlib_async.*` + yeni sentaks testleri

3. Benchmark tek-kaynak temizligi
- Dosyalar: `tests/benchmark_python_compare.py`, `tests/benchmark_python_gate.py`, `main.cpp`
- Artefakt: `build/python_compare.json`

4. Sunucu route prototipi
- Dosyalar: `StdLib/Sunucu.h`, `VM.cpp`
- Testler: `tests/cases/stdlib_server.*` genisletme

## 6) Riskler ve Azaltma

Risk:
- Cok hizli ozellik ekleme, VM parity bozabilir
Azaltma:
- Her ozellik icin `vm-kati` + fallback matrix + yeni case testleri zorunlu

Risk:
- JIT'e erken gecis teknik borc dogurur
Azaltma:
- Once profiling + AOT + GC modernizasyonu

Risk:
- Tam Turkce kimlik global adopsyonu yavaslatabilir
Azaltma:
- Dil Turkce kalir, dokuman/ekosistem iki dilli olur

## 7) Basari Tanimi (2029 Sonu)

- Stable kanalda fallback ihtiyaci yok
- Benchmark medyaninda Python uzerinde kalici ustunluk
- AOT/JIT modlari kullanima acik
- WASM hedefi calisir durumda
- Paket ekosistemi ve topluluk metrikleri global gorunurluk seviyesine cikmis
