#!/usr/bin/env python3
"""ASCII comparison operators map to Turkish comparison keywords."""

from __future__ import annotations

import argparse
import os
import subprocess
import tempfile
from pathlib import Path


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def run_source(binary: Path, source: str) -> tuple[int, str]:
    env = os.environ.copy()
    env.pop("ORHUN_TURKCE_KATI", None)
    with tempfile.TemporaryDirectory(prefix="orhun_ascii_") as tmp:
        path = Path(tmp) / "ornek.oh"
        path.write_text(source, encoding="utf-8")
        proc = subprocess.run(
            [str(binary), str(path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=15,
            env=env,
        )
        return proc.returncode, (proc.stdout + proc.stderr).replace("\r\n", "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="ASCII comparison smoke")
    parser.add_argument("binary", help="Orhun executable")
    args = parser.parse_args()
    binary = Path(args.binary)
    require(binary.exists(), f"Binary not found: {binary}")

    cases = [
        ("eq", "yazdır 1 == 1\nyazdır 1 == 2\n", ["1", "0"]),
        ("neq", "yazdır 1 != 2\nyazdır 1 != 1\n", ["1", "0"]),
        ("lt", "yazdır 1 < 2\nyazdır 2 < 1\n", ["1", "0"]),
        ("gt", "yazdır 2 > 1\nyazdır 1 > 2\n", ["1", "0"]),
        ("if", 'eğer 1 < 2 ise:\n    yaz "ok"\n', ["ok"]),
        ("while", "i olsun 0\nsürece i < 2:\n    yaz i\n    i = i + 1\n", ["0", "1"]),
        ("turkish", "yazdır 1 küçük 2\nyazdır 1 eşit 1\n", ["1", "1"]),
    ]
    for name, source, needles in cases:
        code, out = run_source(binary, source)
        require(code == 0, f"{name}: exit={code}\n{out}")
        for needle in needles:
            require(needle in out, f"{name}: missing {needle!r} in\n{out}")
        print(f"[OK] {name}")

    for name, op in (("le", "<="), ("ge", ">=")):
        code, out = run_source(binary, f"yazdır 1 {op} 2\n")
        require(code != 0, f"{name}: expected rejection\n{out}")
        require(
            "İpucu:" in out and "veya" in out,
            f"{name}: expected teaching hint\n{out}",
        )
        print(f"[OK] {name}-teaches")

    print("ASCII comparison smoke passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
