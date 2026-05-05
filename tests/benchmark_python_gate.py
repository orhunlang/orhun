#!/usr/bin/env python3
import argparse
import json
import statistics
from pathlib import Path


REQUIRED_BENCHES = [
    "fib_recursive",
    "fib_iterative",
    "nbody",
    "spectral_norm",
    "json_loads",
    "string_concat",
    "binary_tree",
    "method_call",
    "matrix_mult",
    "primes",
]


def outputs_match(orhun_out: str, python_out: str) -> bool:
    if orhun_out == python_out:
        return True
    try:
        a = float(orhun_out)
        b = float(python_out)
        tol = 1e-6 * max(1.0, abs(a), abs(b))
        return abs(a - b) <= tol
    except Exception:
        return False


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> int:
    parser = argparse.ArgumentParser(description="Gate python_compare benchmark output")
    parser.add_argument("--json", default="build/python_compare.json", help="Path to python compare json")
    parser.add_argument("--min-median-p50", type=float, default=1.05)
    parser.add_argument("--min-fast-cases", type=int, default=6)
    args = parser.parse_args()

    path = Path(args.json)
    if not path.exists():
        print(f"[FAIL] Missing benchmark file: {path}")
        return 3

    try:
        rows = json.loads(path.read_text(encoding="utf-8"))
    except Exception as ex:
        print(f"[FAIL] Could not parse JSON: {ex}")
        return 3

    try:
        require(isinstance(rows, list) and rows, "benchmark json must be a non-empty list")
        by_name = {str(r.get("bench", "")): r for r in rows}
        missing = [name for name in REQUIRED_BENCHES if name not in by_name]
        require(not missing, f"required benches missing: {', '.join(missing)}")

        speedups = []
        fast_cases = 0
        mismatches = []
        for name in REQUIRED_BENCHES:
            row = by_name[name]
            s = float(row["speedup_p50_x"])
            speedups.append(s)
            if s >= 1.0:
                fast_cases += 1
            if not outputs_match(str(row.get("orhun_out", "")), str(row.get("python_out", ""))):
                mismatches.append(name)

        median_speedup = statistics.median(speedups)
        print(f"[PY-GATE] median_p50={median_speedup:.3f} min={args.min_median_p50:.3f}")
        print(f"[PY-GATE] fast_cases={fast_cases} min={args.min_fast_cases}")

        require(not mismatches, f"output mismatch benches: {', '.join(mismatches)}")
        require(
            median_speedup >= args.min_median_p50,
            f"median speedup below threshold ({median_speedup:.3f} < {args.min_median_p50:.3f})",
        )
        require(
            fast_cases >= args.min_fast_cases,
            f"fast case count below threshold ({fast_cases} < {args.min_fast_cases})",
        )
    except RuntimeError as ex:
        print(f"[FAIL] {ex}")
        return 2

    print("Python compare gate passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

