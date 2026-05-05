#!/usr/bin/env python3
import argparse
import json
import statistics
import subprocess
import time
from pathlib import Path
import shlex


BENCHES = [
    "fib_recursive",
    "nbody",
    "spectral_norm",
    "json_loads",
    "fib_iterative",
    "string_concat",
    "binary_tree",
    "method_call",
    "matrix_mult",
    "primes",
]


def timed_run(cmd: list[str], timeout: float) -> tuple[float, str]:
    start = time.perf_counter()
    proc = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=timeout,
        check=False,
    )
    elapsed_ms = (time.perf_counter() - start) * 1000.0
    out = (proc.stdout + proc.stderr).strip()
    if proc.returncode != 0:
        raise RuntimeError(f"Command failed ({proc.returncode}): {' '.join(cmd)}\n{out}")
    return elapsed_ms, out


def percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    if len(values) == 1:
        return values[0]
    idx = (len(values) - 1) * (p / 100.0)
    lo = int(idx)
    hi = min(lo + 1, len(values) - 1)
    frac = idx - lo
    return values[lo] + (values[hi] - values[lo]) * frac


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


def resolve_python_executable(preferred: str) -> list[str]:
    if preferred.strip():
        return shlex.split(preferred)

    candidates = [["python3"], ["python"], ["py", "-3"]]
    for cand in candidates:
        try:
            proc = subprocess.run(
                cand + ["-c", "print(1)"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=5.0,
                check=False,
            )
            if proc.returncode == 0:
                return cand
        except Exception:
            continue
    raise SystemExit("Python executable not found. Use --python to provide one.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare Orhun VM vs Python benchmarks")
    parser.add_argument("--orhun", default="./orhun_test", help="Orhun executable path")
    parser.add_argument("--python", default="", help="Python executable command")
    parser.add_argument("--repeat", type=int, default=7, help="Measurement repetitions")
    parser.add_argument("--warmup", type=int, default=2, help="Warmup runs")
    parser.add_argument("--timeout", type=float, default=20.0, help="Timeout per run (seconds)")
    parser.add_argument("--json-out", default="", help="Optional JSON output file")
    args = parser.parse_args()

    root = Path("tests/benchmarks/python_compare")
    orhun_bin = Path(args.orhun)
    if not orhun_bin.exists():
        raise SystemExit(f"Orhun binary not found: {orhun_bin}")
    python_cmd = resolve_python_executable(args.python)

    rows = []
    for bench in BENCHES:
        oh = root / f"{bench}.oh"
        py = root / f"{bench}.py"
        if not oh.exists() or not py.exists():
            raise SystemExit(f"Missing benchmark files for {bench}")

        orhun_cmd = [str(orhun_bin), "vm-kati", str(oh)]
        py_cmd = python_cmd + [str(py)]

        for _ in range(args.warmup):
            timed_run(orhun_cmd, args.timeout)
            timed_run(py_cmd, args.timeout)

        orhun_times = []
        py_times = []
        orhun_last = ""
        py_last = ""
        for _ in range(args.repeat):
            t_orhun, out_orhun = timed_run(orhun_cmd, args.timeout)
            t_py, out_py = timed_run(py_cmd, args.timeout)
            orhun_times.append(t_orhun)
            py_times.append(t_py)
            orhun_last = out_orhun
            py_last = out_py

        orhun_times.sort()
        py_times.sort()

        rows.append(
            {
                "bench": bench,
                "orhun_p50_ms": percentile(orhun_times, 50),
                "orhun_p90_ms": percentile(orhun_times, 90),
                "python_p50_ms": percentile(py_times, 50),
                "python_p90_ms": percentile(py_times, 90),
                "speedup_p50_x": percentile(py_times, 50) / max(percentile(orhun_times, 50), 1e-9),
                "speedup_p90_x": percentile(py_times, 90) / max(percentile(orhun_times, 90), 1e-9),
                "orhun_out": orhun_last,
                "python_out": py_last,
            }
        )

    print("| benchmark | orhun p50 ms | python p50 ms | speedup p50 x |")
    print("|---|---:|---:|---:|")
    for row in rows:
        print(
            f"| {row['bench']} | {row['orhun_p50_ms']:.3f} | "
            f"{row['python_p50_ms']:.3f} | {row['speedup_p50_x']:.2f} |"
        )

    speedups = [r["speedup_p50_x"] for r in rows]
    print(f"\nMedian speedup (Python/Orhun, p50): {statistics.median(speedups):.2f}x")

    mismatches = [r for r in rows if not outputs_match(r["orhun_out"], r["python_out"])]
    if mismatches:
        print("\n[warn] Output mismatch detected:")
        for row in mismatches:
            print(f"- {row['bench']}: orhun={row['orhun_out']!r} python={row['python_out']!r}")

    if args.json_out:
        Path(args.json_out).write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\nJSON report: {args.json_out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
