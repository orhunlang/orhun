#!/usr/bin/env python3
import argparse
import os
import subprocess
import tempfile
from pathlib import Path


def run_case(binary: Path, source: str, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory(prefix="orhun_ffi_policy_") as tmp:
        src = Path(tmp) / "ffi_policy.oh"
        src.write_text(source, encoding="utf-8")
        return subprocess.run(
            [str(binary), str(src)],
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
    parser = argparse.ArgumentParser(description="Orhun FFI policy smoke test")
    parser.add_argument("binary", help="Orhun executable")
    args = parser.parse_args()

    binary = Path(args.binary)
    if not binary.exists():
        raise SystemExit(f"Binary not found: {binary}")

    base_env = dict(os.environ)
    base_env.pop("ORHUN_FFI_POLICY", None)
    base_env.pop("ORHUN_FFI_ALLOWLIST", None)
    base_env["ORHUN_CHANNEL"] = "stable"

    unknown_lib = 'ffi.yukle("orhun_bilinmeyen_ffi_kitaplik_42.dll")\n'

    stable_allowlist = run_case(binary, unknown_lib, base_env)
    stable_text = (stable_allowlist.stdout + stable_allowlist.stderr).lower()
    require(stable_allowlist.returncode != 0, "stable allowlist mode should block unknown library")
    require("allowlist" in stable_text, "stable allowlist rejection message missing")

    off_env = dict(base_env)
    off_env["ORHUN_FFI_POLICY"] = "off"
    off_case = run_case(binary, unknown_lib, off_env)
    off_text = (off_case.stdout + off_case.stderr).lower()
    require(off_case.returncode != 0, "ffi policy off must reject ffi usage")
    require("ffi politikasi kapali" in off_text, "ffi off rejection message missing")

    full_env = dict(base_env)
    full_env["ORHUN_FFI_POLICY"] = "full"
    full_case = run_case(binary, unknown_lib, full_env)
    full_text = (full_case.stdout + full_case.stderr).lower()
    require(full_case.returncode != 0, "full mode should fail for unknown library load")
    require("allowlist" not in full_text, "full mode must not fail with allowlist message")
    require("basarisiz" in full_text or "yuklenemedi" in full_text, "full mode should fail on actual library load")

    print("FFI policy smoke passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
