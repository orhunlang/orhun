# Orhun State Snapshot - 2026-02-17

This snapshot freezes the working baseline used for the 6-month roadmap.

## Identity

- date: `2026-02-17`
- branch: `master`
- head_short: `a22b1ba`
- head_full: `a22b1baf63b024f468ec4f855bb7ba35848ae04e`
- version_file: `VERSION` -> `0.8.0`
- cli_version: `orhun surum` -> `Orhun v0.8.0 (insa 50)`
- tracked_changes_snapshot: `changed_entries=218`

## Working Assumptions

- This snapshot follows the current working tree, not only committed `HEAD`.
- Test execution is intentionally skipped in this update wave.
- Stable channel compatibility must remain additive-only.

## CI Surface at Snapshot Time

- workflows:
  - `.github/workflows/ci.yml`
  - `.github/workflows/nightly.yml`
- matrix:
  - windows-latest
  - ubuntu-latest
  - macos-latest
- existing quality areas:
  - functional tests
  - vm parity
  - fallback matrix
  - benchmark contract/pipeline smoke
  - fuzz smoke
  - lsp smoke
  - lock/ffi/dx smokes

## Benchmark Baseline Files

- `benchmarks_new.json`
- `benchmarks_optimized.json`
- `build/benchmark_results.jsonl` (pipeline-generated)
- `build/python_compare.json` (pipeline-generated)

## Strategic Defaults

- strategy: `guvenilir cekirdek`
- compatibility: `stable kati uyum`
- kpi mode: `dengeli`
- horizon: `6 ay / 3 faz`

