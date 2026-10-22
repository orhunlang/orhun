# Orhun Known Issues

This list tracks behavior that is intentionally incomplete or likely to change
before `1.0`. It is part of the stability contract: anything not listed here
should be treated as a bug.

## Language / Runtime

- Structural English syntax is **not** supported. English keyword aliases map
  tokens only; `if cond ise:` still requires the Turkish `ise` particle.
- `fn`, `func`, `def`, `let`, `var` are **not** English aliases (identifier
  collision risk).
- Booleans print as `1` / `0` rather than `doğru` / `yanlış` in `yazdır`.
- Comparison surface is Turkish (`küçük`, `büyük`, `eşit`); ASCII `==`, `!=`,
  `<`, `>` are supported aliases. `<=` and `>=` are rejected with a teaching
  hint (use `küçük`/`büyük` plus `veya`).
- Closure capture is implemented and regression-guarded, but exotic nested
  mutation edge cases may still differ between interpreter and VM until the
  next parity sweep.
- Pre-1.0 versions may change language behavior with a documented migration
  entry in `docs/MIGRATION_GUIDE.md`.

## Tooling / Packaging

- Official binaries are published only through GitHub Releases; local
  `*.exe` files are not tracked in git.
- Platform code-signing and native installers are still outstanding before
  a production-grade `2.1.0` bar.
- Package lock verification requires a project lock; `doctor` reports
  `lock_exists: false` on a bare source checkout.

## Self-Hosting

- The serialization bridge and C++ runtime remain bootstrap dependencies even
  when the compiler frontend/IR is written in Orhun.

## How To Report

Open a GitHub issue for bugs. For vulnerabilities, follow `SECURITY.md`
(private report to `orhunlang@gmail.com`).
