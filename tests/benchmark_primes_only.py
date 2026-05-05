#!/usr/bin/env python3
import argparse
import json
import statistics
import subprocess
import time
from pathlib import Path
import shlex


BENCHES = [
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
    parser.add_argument("--orhun", default="./orhun.exe", help="Orhun executable path")
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

        print(f"Benchmark: {bench}")
        print(f"Orhun P50: {percentile(orhun_times, 50):.3f} ms")
        print(f"Python P50: {percentile(py_times, 50):.3f} ms")
        print(f"Speedup: {percentile(py_times, 50) / max(percentile(orhun_times, 50), 1e-9):.2f}x")
        print("-" * 40)
        
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
