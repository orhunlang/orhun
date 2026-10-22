# Orhun Compatibility Policy

This policy is the operational companion to `docs/SPEC.md` (language contract),
`docs/DEPRECATION_POLICY.md` (timeline), and `docs/VERSIONING.md` (numbers).

## Channels

| Channel | Stability intent |
| --- | --- |
| `nightly` | Fast-moving; behavior may change with warnings first. |
| `beta` | Near-stable candidate; breaking changes are rare and documented. |
| `stable` | Patch releases do not break documented programs. |

## What Is Covered After 1.0

1. **Source language** — Turkish keywords, operators, capture model, module
   include rules, and diagnostics categories defined in `docs/SPEC.md`.
2. **CLI contract** — documented commands and their Turkish/English alias pairs
   listed in `docs/SPEC.md` § CLI Contract.
3. **Artifacts** — `.obc` metadata contracts and packaged-executable trailer
   versions that already ship (`orhun-obc-v2`, `ORHNPKG2`).
4. **Stdlib modules** — public entry points of `StdLib/orhun/*.oh` as exercised
   by `tests/cases/stdlib_orhun_*.oh`.

## What Is Not Covered

- Exact diagnostic wording (except that teaching hints remain present for the
  error classes already guarded by smoke tests).
- Internal C++ class layout, opcode numbering without a versioned IR contract,
  and private helpers.
- Performance numbers (gates may tighten; regressions are bugs, not breaks).
- Pre-1.0 experimental surfaces explicitly listed in `docs/KNOWN_ISSUES.md`.

## English Keyword Aliases

- Aliases are a **non-strict** convenience. They may grow additively.
- Aliases never replace Turkish keywords in strict mode.
- Short names that collide with realistic identifiers (`fn`, `func`, `def`,
  `let`, `var`) will not be added as aliases.

## Verification Before A Compatibility Claim

```text
tests/run_tests.ps1
tests/vm_parity.ps1
python tests/teaching_hint_smoke.py ./build/orhun_test.exe
python tests/english_alias_smoke.py ./build/orhun_test.exe
python tests/version_consistency_smoke.py ./build/orhun_test.exe
python tests/roadmap_smoke.py ./build/orhun_test.exe
```

## Reporting A Break

Open a GitHub issue labeled `compatibility` with:

- Orhun version and channel
- Minimal source that used to work
- Actual vs expected behavior
- Whether `ORHUN_TURKCE_KATI=1` changes the outcome
