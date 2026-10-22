#!/usr/bin/env python3
"""1.0 readiness checklist smoke — aggregates stability gates."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def run_py(script: str, *args: str) -> None:
    cmd = [sys.executable, script, *args]
    proc = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"{script} failed rc={proc.returncode}\n{proc.stdout}{proc.stderr}"
        )
    print(f"[OK] {Path(script).name}")


def main() -> int:
    parser = argparse.ArgumentParser(description="1.0 readiness checklist")
    parser.add_argument("binary", help="Orhun executable")
    args = parser.parse_args()
    binary = Path(args.binary)
    require(binary.exists(), f"Binary not found: {binary}")
    repo = Path.cwd()

    # Documentation contract.
    for doc in (
        "docs/SPEC.md",
        "docs/MIGRATION_GUIDE.md",
        "docs/KNOWN_ISSUES.md",
        "docs/COMPATIBILITY_POLICY.md",
        "docs/DEPRECATION_POLICY.md",
        "docs/VERSIONING.md",
        "docs/PROJECT_STATUS.md",
        "docs/BEGINNER_GUIDE.md",
    ):
        require((repo / doc).exists(), f"Missing stability doc: {doc}")
    print("[OK] stability-docs")

    spec = (repo / "docs" / "SPEC.md").read_text(encoding="utf-8")
    require("## 1.0 Stability Checklist" in spec, "SPEC missing 1.0 checklist")
    require("## Compatibility Rules" in spec, "SPEC missing compatibility rules")
    print("[OK] spec-structure")

    version = (repo / "VERSION").read_text(encoding="utf-8").strip()
    header = (repo / "Interpreter.h").read_text(encoding="utf-8")
    match = re.search(r'#define\s+ORHUN_SURUM\s+"([^"]+)"', header)
    require(match is not None, "Interpreter.h missing ORHUN_SURUM")
    require(match.group(1) == version, "VERSION != ORHUN_SURUM")
    readme = (repo / "README.md").read_text(encoding="utf-8")
    require(f"Current version: `{version}`" in readme, "README version mismatch")
    print(f"[OK] version-aligned ({version})")

    run_py("tests/version_consistency_smoke.py", str(binary))
    run_py("tests/project_status_smoke.py")
    run_py("tests/case_manifest_smoke.py")
    run_py("tests/spec_keyword_contract_smoke.py")
    run_py("tests/cli_contract_smoke.py", str(binary))
    run_py("tests/teaching_hint_smoke.py", str(binary))
    run_py("tests/english_alias_smoke.py", str(binary))
    run_py("tests/known_gap_smoke.py", str(binary))
    run_py("tests/beginner_docs_smoke.py")
    run_py("tests/benchmark_pipeline_smoke.py")
    run_py("tests/perf_baseline_smoke.py", str(binary))

    print("1.0 readiness checklist smoke passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
