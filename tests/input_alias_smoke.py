#!/usr/bin/env python3
import argparse
import subprocess
import tempfile
from pathlib import Path


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def run(args: list[str], cwd: Path, stdin: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=cwd,
        input=stdin,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="input alias smoke test")
    parser.add_argument("binary", help="Orhun executable path")
    args = parser.parse_args()

    repo = Path(__file__).resolve().parents[1]
    binary = Path(args.binary).resolve()
    require(binary.exists(), f"Binary not found: {binary}")

    with tempfile.TemporaryDirectory(prefix="orhun_input_alias_") as tmp:
        source = Path(tmp) / "oku_alias.oh"
        source.write_text(
            'ad olsun oku("Ad? ")\n'
            'yaz "Merhaba, " + ad\n',
            encoding="utf-8",
            newline="\n",
        )

        for mode in ([], ["vm-kati"], ["yorumla"]):
            proc = run([str(binary), *mode, str(source)], repo, "Ada\n")
            label = " ".join(mode) or "default"
            require(
                proc.returncode == 0,
                f"oku alias failed in {label}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}",
            )
            require(
                proc.stdout.replace("\r\n", "\n") == "Ad? Merhaba, Ada\n",
                f"oku alias output mismatch in {label}: {proc.stdout!r}",
            )

    print("Input alias smoke passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
