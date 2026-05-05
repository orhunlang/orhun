#!/usr/bin/env python3
import argparse
import os
import subprocess
from pathlib import Path


def run(binary: Path, args: list[str], env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(binary)] + args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> int:
    parser = argparse.ArgumentParser(description="Fallback smoke for ORH-COMP compiler errors")
    parser.add_argument("binary", help="Orhun executable")
    parser.add_argument(
        "--case",
        default="tests/cases/closure_missing_feature.oh",
        help="Case expected to trigger ORH-COMP fallback path",
    )
    args = parser.parse_args()

    binary = Path(args.binary)
    if not binary.exists():
        raise SystemExit(f"Binary not found: {binary}")

    case = Path(args.case)
    if not case.exists():
        raise SystemExit(f"Case not found: {case}")

    env_base = dict(os.environ)
    env_base["ORHUN_CHANNEL"] = "stable"

    env_off = dict(env_base)
    env_off["ORHUN_VM_FALLBACK"] = "0"
    p_off = run(binary, [str(case)], env_off)
    text_off = (p_off.stdout + p_off.stderr).lower()
    require(p_off.returncode != 0, "fallback=0 should fail on ORH-COMP input")
    require("orh-comp-" in text_off, "fallback=0 run must expose ORH-COMP marker")

    env_on = dict(env_base)
    env_on["ORHUN_VM_FALLBACK"] = "1"
    p_on = run(binary, [str(case)], env_on)
    text_on = (p_on.stdout + p_on.stderr).lower()
    require(p_on.returncode == 0, "fallback=1 should recover via interpreter")
    require("orh-comp-" not in text_on, "fallback=1 output should not surface ORH-COMP error")

    p_strict = run(binary, ["vm-kati", str(case)], env_on)
    text_strict = (p_strict.stdout + p_strict.stderr).lower()
    require(p_strict.returncode != 0, "vm-kati should fail for unsupported VM construct")
    require("orh-comp-" in text_strict, "vm-kati failure should expose ORH-COMP marker")

    print("Fallback ORH-COMP smoke passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

