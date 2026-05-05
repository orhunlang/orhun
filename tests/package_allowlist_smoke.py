#!/usr/bin/env python3
import argparse
import os
import subprocess
import tempfile
from pathlib import Path


def run_cmd(args: list[str], cwd: Path, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=str(cwd),
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
    parser = argparse.ArgumentParser(description="Package source allowlist smoke test")
    parser.add_argument("binary", help="Orhun executable")
    args = parser.parse_args()

    binary = Path(args.binary).resolve()
    if not binary.exists():
        raise SystemExit(f"Binary not found: {binary}")

    remote = "https://example.com/orhun/nonexistent-package.git"

    with tempfile.TemporaryDirectory(prefix="orhun_pkg_allowlist_") as tmp:
        root = Path(tmp)

        env_default = dict(os.environ)
        env_default.pop("ORHUN_PAKET_ALLOWLIST", None)
        blocked = run_cmd(
            [str(binary), "paket", "kur", remote, "ornek_paket"],
            root,
            env_default,
        )
        blocked_text = (blocked.stdout + blocked.stderr).lower()
        require(blocked.returncode != 0, "unallowlisted host should fail")
        require("allowlist disinda" in blocked_text, "missing allowlist rejection message")

        env_allowed = dict(env_default)
        env_allowed["ORHUN_PAKET_ALLOWLIST"] = "example.com"
        allowed = run_cmd(
            [str(binary), "paket", "kur", remote, "ornek_paket2"],
            root,
            env_allowed,
        )
        allowed_text = (allowed.stdout + allowed.stderr).lower()
        require(allowed.returncode != 0, "dummy remote should still fail on clone")
        require("allowlist disinda" not in allowed_text, "host should pass allowlist stage when env allows it")
        require("paket indirilemedi" in allowed_text or "clone" in allowed_text, "failure should move to git clone stage")

    print("Package allowlist smoke passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

