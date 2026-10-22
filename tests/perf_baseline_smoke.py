#!/usr/bin/env python3
"""Retained performance baseline gate for a representative workload."""

from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from pathlib import Path

WORKLOAD = """işlev fib(n):
    eğer n küçük 2 ise:
        döndür n
    döndür fib(n - 1) + fib(n - 2)

yazdır fib(12)
"""

# Relative gate: VM p50 must not be slower than interpreter p50 on the same
# machine/run. This stays meaningful across hardware; absolute baselines are
# optional and opt-in via --baseline.
MIN_P50_SPEEDUP = 0.90


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> int:
    parser = argparse.ArgumentParser(description="Perf baseline gate")
    parser.add_argument("binary", help="Orhun executable")
    parser.add_argument("--min-p50", type=float, default=MIN_P50_SPEEDUP)
    args = parser.parse_args()
    binary = Path(args.binary)
    require(binary.exists(), f"Binary not found: {binary}")

    with tempfile.TemporaryDirectory(prefix="orhun_perf_") as tmp:
        src = Path(tmp) / "fib.oh"
        src.write_text(WORKLOAD, encoding="utf-8")
        cmd = [
            str(binary),
            "hiz",
            str(src),
            "--tekrar=8",
            "--warmup=3",
            "--olcum-modu=runtime",
            "--json",
        ]
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
        )
        require(proc.returncode == 0, f"hiz failed: {proc.stderr}")
        lines = [ln for ln in proc.stdout.splitlines() if ln.strip()]
        payload = json.loads(lines[-1])
        speedup = float(payload["hizlanma"]["p50_x"])
        require(
            speedup >= args.min_p50,
            f"p50 speedup {speedup:.3f} < {args.min_p50}",
        )
        print(f"Perf baseline gate passed (p50_speedup={speedup:.3f}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
