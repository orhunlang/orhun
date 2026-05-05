#!/usr/bin/env python3
import argparse
import os
import subprocess
from pathlib import Path


def run_doctor(binary: Path, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(binary), "doctor"],
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


def expect_fallback(binary: Path, channel: str, expected_open: bool, override: str | None = None) -> None:
    env = dict(os.environ)
    env["ORHUN_CHANNEL"] = channel
    if override is None:
        env.pop("ORHUN_VM_FALLBACK", None)
    else:
        env["ORHUN_VM_FALLBACK"] = override

    proc = run_doctor(binary, env)
    output = proc.stdout + proc.stderr
    require(proc.returncode in (0, 2), f"doctor returned unexpected rc={proc.returncode}")

    expect_flag = "acik" if expected_open else "kapali"
    require(
        f"VM fallback varsayilan durumu: {expect_flag}" in output,
        f"fallback expectation mismatch for channel={channel} override={override}",
    )
    require(f"Release channel: {channel}" in output, f"release channel mismatch for {channel}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Orhun fallback matrix test")
    parser.add_argument("binary", help="Orhun executable")
    args = parser.parse_args()

    binary = Path(args.binary)
    if not binary.exists():
        raise SystemExit(f"Binary not found: {binary}")

    expect_fallback(binary, "stable", False)
    expect_fallback(binary, "beta", True)
    expect_fallback(binary, "nightly", True)
    expect_fallback(binary, "dev", True)
    expect_fallback(binary, "nightly", False, override="0")
    expect_fallback(binary, "stable", True, override="1")

    print("Fallback matrix passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
