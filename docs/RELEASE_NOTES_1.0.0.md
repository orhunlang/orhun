# Orhun 1.0.0 Release Notes

Orhun 1.0.0 is the first stable language contract release.

## Stability Promise

- `docs/SPEC.md` is the language contract.
- `docs/COMPATIBILITY_POLICY.md` defines what stays stable across patch releases.
- `docs/DEPRECATION_POLICY.md` requires warn → opt-in → remove for breaks.
- `docs/KNOWN_ISSUES.md` lists accepted gaps so they are not treated as bugs.

## Highlights Since 0.9.0

### Compiler as a Teacher

Common beginner errors include Turkish `İpucu` / `Örnek` fix lines.

### English Keyword Aliases (non-strict)

`if`, `print`, `function`, `return`, `while`, `for`/`in`, and related keywords
normalize to Turkish tokens. `ORHUN_TURKCE_KATI=1` rejects aliases and teaches
the Turkish form.

### ASCII Comparison And Logic Operators

`==`, `!=`, `<`, `>`, `<=`, `>=` and unary `!` map onto `eşit`,
`eşit_değil`, `büyük`, `küçük`, and `değil`.

### Discoverable CLI

`orhun yardim` / `orhun help` prints a command summary.

### Release Gates

`tests/release_readiness_smoke.py` aggregates version alignment, teaching,
aliases, ASCII operators, CLI contract, benchmark manifest, and a relative
performance floor. CI runs these on Windows, Linux, and macOS.

## Upgrade From 0.9.x

No breaking source changes. See `docs/MIGRATION_GUIDE.md` for additive
operator and alias notes.

## Known Issues

See `docs/KNOWN_ISSUES.md`. Code-signing and native installers remain on the
`2.1.0` product bar.

## Verification

- Full case suite green
- VM parity: 153 fixtures, 0 failures
- Roadmap smoke: 34/34
- Fuzz smoke: no crashes
- Release readiness checklist green
