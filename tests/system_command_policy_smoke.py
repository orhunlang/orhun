#!/usr/bin/env python3
import argparse
import os
import subprocess
import tempfile
from pathlib import Path


def run_case(binary: Path, source: str, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory(prefix="orhun_syscmd_policy_") as tmp:
        src = Path(tmp) / "syscmd_policy.oh"
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
    parser = argparse.ArgumentParser(description="System command policy smoke test")
    parser.add_argument("binary", help="Orhun executable")
    args = parser.parse_args()

    binary = Path(args.binary)
    if not binary.exists():
        raise SystemExit(f"Binary not found: {binary}")

    base_env = dict(os.environ)
    base_env.pop("ORHUN_UNSAFE", None)
    base_env.pop("ORHUN_SYSTEM_UNSAFE", None)

    blocked_chars = [";", "|", "&", "<", ">", "`", "$", "\"", "'"]
    for ch in blocked_chars:
        source_char = r"\"" if ch == '"' else ch
        src = f'sistem.komut("echo a{source_char}echo b")\n'
        proc = run_case(binary, src, base_env)
        text = (proc.stdout + proc.stderr).lower()
        require(proc.returncode != 0, f"restricted mode should block char: {ch!r}")
        require("kisitli modda tehlikeli karakter" in text, f"missing block message for char: {ch!r}")

    safe = run_case(binary, 'sistem.komut("whoami")\n', base_env)
    require(safe.returncode == 0, "safe command should pass in restricted mode")

    unsafe_env = dict(base_env)
    unsafe_env["ORHUN_UNSAFE"] = "1"
    relaxed = run_case(binary, 'sistem.komut("echo a; echo b")\n', unsafe_env)
    text_relaxed = (relaxed.stdout + relaxed.stderr).lower()
    require("kisitli modda tehlikeli karakter" not in text_relaxed, "ORHUN_UNSAFE should disable restricted-char rejection")

    print("System command policy smoke passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
