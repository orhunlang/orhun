# Orhun 0.9.0 Release Notes

Date: development line (pre-1.0)

## Highlights

### Compiler as a Teacher

Common beginner errors now include fix hints:

```text
İşlev başlığından sonra ':' bekleniyor.
  İpucu: İşlev tanımı iki nokta ile biter.
  Örnek: işlev topla(a, b):
```

- English keyword mistakes map to the Turkish equivalent
  (`if` → `eğer`, `print` → `yazdır`, …).
- Undefined names explain how to declare (`ad olsun deger`).
- Keyword tokens no longer receive fake Levenshtein suggestions.

### English Keyword Alias Bridge

Default mode normalizes selected English keywords to Turkish tokens:

| English | Orhun |
| --- | --- |
| `if` | `eğer` |
| `else` | `değilse` |
| `while` | `sürece` |
| `for` / `in` | `her` / `içinde` |
| `function` | `işlev` |
| `return` | `döndür` |
| `print` / `write` | `yazdır` |
| `true` / `false` | `doğru` / `yanlış` |

Structural particles stay Turkish (`if cond ise:`). Enable
`ORHUN_TURKCE_KATI=1` to reject aliases and receive teaching hints.

### ASCII Comparison Operators

`==`, `!=`, `<`, `>`, `<=`, `>=` map to `eşit`, `eşit_değil`, `büyük`,
`küçük` and the non-strict relations. Turkish keywords remain primary.

### Discoverable CLI

`orhun yardim` / `orhun help` prints a command summary.

### Benchmark Manifest

`tests/benchmarks/python_compare/benchmarks.txt` is the source of truth for
Python-compare workloads, including the new `function_call` benchmark.

## Upgrade Notes

See `docs/MIGRATION_GUIDE.md` section *Öğretici Hata İpuçları ve İngilizce
Anahtar Alias'ları (0.9.0)*.

## Verification

- Full case suite green
- VM parity: 153 fixtures
- New smokes: `teaching_hint_smoke.py`, `english_alias_smoke.py`
