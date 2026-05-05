#!/usr/bin/env python3
import argparse
import json
import subprocess
from pathlib import Path


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> int:
    parser = argparse.ArgumentParser(description="Doctor JSON contract smoke")
    parser.add_argument("binary", help="Orhun executable")
    args = parser.parse_args()

    binary = Path(args.binary)
    if not binary.exists():
        raise SystemExit(f"Binary not found: {binary}")

    proc = subprocess.run(
        [str(binary), "doctor", "--json"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    require(proc.returncode in (0, 2), f"doctor returned unexpected rc={proc.returncode}")

    lines = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    require(lines, "doctor --json output is empty")
    try:
        payload = json.loads(lines[-1])
    except Exception as ex:
        raise RuntimeError(f"doctor --json is not valid JSON: {ex}") from ex

    for key in ("version", "commit", "channel", "fallback_default", "ci_profiles", "security_mode"):
        require(key in payload, f"doctor json missing key: {key}")

    sec = payload.get("security_mode", {})
    require(isinstance(sec, dict), "security_mode must be an object")
    require("ffi_policy_default" in sec, "security_mode.ffi_policy_default missing")
    require("system_command_restricted_default" in sec, "security_mode.system_command_restricted_default missing")

    print("Doctor JSON smoke passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

