#!/usr/bin/env python3
import argparse
import subprocess
from pathlib import Path


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def run(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=cwd,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="run public examples")
    parser.add_argument("binary", help="Orhun executable path")
    args = parser.parse_args()

    repo = Path(__file__).resolve().parents[1]
    binary = Path(args.binary).resolve()
    require(binary.exists(), f"Binary not found: {binary}")

    examples = sorted((repo / "examples").glob("*.oh"))
    require(examples, "No examples found")

    for example in examples:
        proc = run([str(binary), str(example)], repo)
        require(
            proc.returncode == 0,
            f"Example failed: {example.name}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}",
        )

    merhaba = (repo / "examples" / "merhaba.oh").read_text(encoding="utf-8")
    require(
        'yaz "Merhaba, Orhun!"' in merhaba,
        "merhaba example should use the beginner-friendly yaz command",
    )

    kolay = (repo / "examples" / "kolay_baslangic.oh").read_text(
        encoding="utf-8"
    )
    for snippet in (
        "aralik(1, 6)",
        "ilk(sayilar)",
        "son(sayilar)",
        "dolu_mu",
        "her sayi içinde sayilar:",
        "[x * x için x içinde sayilar]",
    ):
        require(snippet in kolay, f"kolay_baslangic should include {snippet}")

    print(f"Examples smoke passed ({len(examples)} examples).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
