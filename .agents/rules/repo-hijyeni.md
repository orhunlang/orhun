# Orhun Depo Hijyeni ve Katkı Kuralları

Bu belge, Orhun projesinde çalışan tüm geliştiriciler ve yapay zeka ajanları (Antigravity, MiMo, Cline vb.) için bağlayıcı temel kuralları tanımlar.

---

## 1. Git Dosya Hijyeni (Ne Girer, Ne Girmez?)

* **Repoya Kesinlikle Girenler (Kaynak Kodlar):**
  * C++ çekirdek kaynak ve başlık dosyaları (`*.cpp`, `*.h`)
  * Saf Orhun standart kütüphane ve dil dosyaları (`StdLib/orhun/*.oh`)
  * Test süitleri ve beklenen çıktılar (`tests/`, `tests/cases/*.oh`, `*.expected.txt`)
  * Dokümantasyon ve spesifikasyonlar (`docs/`, `*.md`, `LICENSE`, `SECURITY.md`)
  * CI/CD iş akışları ve derleme betikleri (`.github/workflows/`, `*.ps1`, `*.sh`, `*.py`)

* **Repoya ASLA Girmeyenler (Yerel / Geçici Dosyalar):**
  * Derlenmiş çalıştırılabilir dosyalar (`*.exe`, `*.dll`, `*.so`, `*.dylib`)
  * Ara derleme nesneleri (`*.obj`, `*.o`, `*.pdb`, `*.ilk`)
  * Geçici derleme ve test dizinleri (`build/`, `coverage/`, `test-work/`, `__pycache__/`)
  * Yerel yapılandırmalar, kişisel API anahtarları veya ortam değişkenleri (`.env`)

---

## 2. İkili Dağıtımı ve GitHub Releases

* Derlenmiş ikili dosyalar (`orhun.exe`) **asla git deposuna commit edilmez**.
* Dağıtılacak resmi ikili dosyalar, sürüm etiketleri (`v0.8.0`, `v0.9.0` vb.) tetiklendiğinde CI/CD boru hattı üzerinden **GitHub Releases** sekmesine bağımsız sürüm varlıkları (release assets) olarak yüklenir.
* Doğrulama ve paketleme için `tools/release_package.py` ve `orhun paketli-dogrula` araçları kullanılır.

---

## 3. Git Commit Standartları ve Kimlik

* **Yazar Kimliği:** Tüm commit'ler `yoreva-1` hesabı ve ilişkili e-posta adresiyle imzalanır/gönderilir.
* **Commit Mesaj Formatı (Conventional Commits):**
  * `feat: ...` $\rightarrow$ Yeni bir dil özelliği, standart kütüphane fonksiyonu veya yetenek eklendiğinde.
  * `fix: ...` $\rightarrow$ Hata düzeltmelerinde (parser, VM, CLI veya bellek sızıntıları).
  * `perf: ...` $\rightarrow$ Yorumlayıcı, derleyici veya sanal makine hızlandırmalarında.
  * `test: ...` $\rightarrow$ Yeni test vakaları veya benchmark iş yükleri eklendiğinde.
  * `docs: ...` $\rightarrow$ Yol haritası, şartname veya kullanım kılavuzu güncellemelerinde.
  * `build: ...` $\rightarrow$ Derleyici bayrakları, CI boru hatları veya release betikleri değişikliklerinde.

---

## 4. C++ Derleme Kuralı (Windows / MinGW)

MinGW GCC ortamlarında linker uyumsuzluğunu (`cannot find 'ld'`) engellemek için `-fuse-ld=bfd` bayrağı mutlaka kullanılmalıdır:

```powershell
g++ -fuse-ld=bfd -std=c++17 -Wall -Wextra -pedantic -O2 -DNDEBUG main.cpp Lexer.cpp Parser.cpp Interpreter.cpp Chunk.cpp Compiler.cpp VM.cpp -o build/orhun_test.exe
```

---

## 5. Doğrulama ve Test Kapısı

Herhangi bir commit öncesinde ilgili test kapıları yeşil olmalıdır:
* Temel dil testleri: `powershell -ExecutionPolicy Bypass -File tests/run_tests.ps1 -Output build/orhun_test.exe`
* Parite denetimi: `powershell -ExecutionPolicy Bypass -File tests/vm_parity.ps1 -Output build/orhun_test.exe`
* Benchmark bütünlüğü: `python tests/benchmark_pipeline_smoke.py`
* Yol haritası regresyon testi: `python tests/roadmap_smoke.py ./build/orhun_test.exe`
