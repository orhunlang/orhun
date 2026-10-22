#!/usr/bin/env python3
"""CLI contract smoke: documented commands respond as expected."""

from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from pathlib import Path


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def run(binary: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(binary), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="CLI contract smoke")
    parser.add_argument("binary", help="Orhun executable")
    args = parser.parse_args()
    binary = Path(args.binary)
    require(binary.exists(), f"Binary not found: {binary}")

    proc = run(binary, "surum")
    require(proc.returncode == 0, f"surum failed: {proc.stderr}")
    require("Orhun v" in proc.stdout, f"surum output unexpected: {proc.stdout}")
    print("[OK] surum")

    proc = run(binary, "yardim")
    require(proc.returncode == 0, f"yardim failed: {proc.stderr}")
    for needle in (
        "vm-kati",
        "doctor",
        "İpucu",
        "ORHUN_TURKCE_KATI",
        "docs/SPEC.md",
    ):
        require(needle in proc.stdout, f"yardim missing {needle!r}")
    print("[OK] yardim")

    proc = run(binary, "help")
    require(proc.returncode == 0, f"help alias failed: {proc.stderr}")
    require("Orhun v" in proc.stdout, "help alias should print version header")
    print("[OK] help-alias")

    proc = run(binary, "doctor", "--json")
    require(proc.returncode == 0, f"doctor --json failed: {proc.stderr}")
    payload = json.loads(proc.stdout.strip().splitlines()[-1])
    require(payload.get("status") == "ready", f"doctor status: {payload}")
    require("security_mode" in payload, "doctor missing security_mode")
    print("[OK] doctor-json")

    with tempfile.TemporaryDirectory(prefix="orhun_cli_") as tmp:
        src = Path(tmp) / "ornek.oh"
        src.write_text('yaz "cli"\n', encoding="utf-8")

        proc = run(binary, str(src))
        require(proc.returncode == 0 and "cli" in proc.stdout, f"run failed: {proc}")
        print("[OK] run-file")

        proc = run(binary, "lex", str(src), "--json")
        require(proc.returncode == 0, f"lex failed: {proc.stderr}")
        require("yaz" in proc.stdout or "token" in proc.stdout.lower(), "lex json empty")
        print("[OK] lex-json")

        proc = run(binary, "fmt", str(src), "--check")
        require(
            proc.returncode in (0, 1),
            f"fmt --check unexpected rc={proc.returncode}: {proc.stderr}",
        )
        out = proc.stdout + proc.stderr
        require(
            "Bicim" in out or "Biçim" in out or proc.returncode == 0,
            f"fmt --check output unexpected: {out}",
        )
        print("[OK] fmt-check")

        proc = run(binary, "lint", str(src))
        require(proc.returncode == 0, f"lint failed: {proc.stderr}")
        print("[OK] lint")

    print("CLI contract smoke passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
