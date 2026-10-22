# Orhun 1.0 Cheat Sheet

Quick reference for the language contract. Full rules: `docs/SPEC.md`.

## Declarations

```orhun
ad olsun 1
x olsun 2, y olsun 3          # çoklu
işlev f(a, b):
    döndür a + b
tip Nokta:
    alan x
```

## Control Flow

```orhun
eğer koşul ise:
    ...
değilse eğer diğer ise:
    ...
değilse:
    ...

sürece koşul:
    ...

tekrarla 3 kez:
    ...

her oge içinde liste:
    ...
```

Karşılaştırma: `küçük`, `büyük`, `eşit` veya ASCII ` < > == != `.

## Collections

```orhun
liste olsun [1, 2, 3]
sozluk olsun {"ad": "Orhun"}
yaz liste[0]
yaz liste[0:2]
yaz sozluk?.ad
```

## Error Handling

```orhun
deneme:
    riskli()
yakala hata:
    yaz hata
```

## Teaching Diagnostics

Mistakes print `İpucu` / `Örnek` lines. Example:

```text
İşlev başlığından sonra ':' bekleniyor.
  İpucu: İşlev tanımı iki nokta ile biter.
  Örnek: işlev topla(a, b):
```

## English Aliases (non-strict)

| English | Orhun |
| --- | --- |
| `if` / `else` | `eğer` / `değilse` |
| `while` / `for` / `in` | `sürece` / `her` / `içinde` |
| `function` / `return` | `işlev` / `döndür` |
| `print` | `yazdır` |
| `true` / `false` | `doğru` / `yanlış` |

Strict mode: `ORHUN_TURKCE_KATI=1`.

## CLI

```bash
orhun yardim
orhun dosya.oh
orhun vm-kati dosya.oh
orhun doctor --json
orhun surum
```

## Safety Defaults

- `sistem.komut` restricted
- FFI `allowlist`
- package source allowlist
