#!/usr/bin/env python3
import argparse
import json
import subprocess
import tempfile
from pathlib import Path


def run_cmd(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def parse_last_json(text: str):
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        raise RuntimeError("json output is empty")
    return json.loads(lines[-1])


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def orhun_string(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def normalized(tokens: list[dict], include_position: bool) -> list[dict]:
    keys = ("tur", "deger", "satir", "sutun") if include_position else ("tur", "deger")
    return [{key: token.get(key) for key in keys} for token in tokens]


def compare_case(binary: Path, repo: Path, source: str, include_position: bool) -> None:
    with tempfile.TemporaryDirectory(prefix="orhun_lexer_parity_") as tmp:
        root = Path(tmp)
        source_file = root / "case.oh"
        driver_file = root / "driver.oh"
        source_file.write_text(source, encoding="utf-8", newline="\n")

        cxx_proc = run_cmd([str(binary), "lex", str(source_file), "--json"], repo)
        require(
            cxx_proc.returncode == 0,
            f"C++ lexer command failed:\nSTDOUT:\n{cxx_proc.stdout}\nSTDERR:\n{cxx_proc.stderr}",
        )
        cxx_payload = parse_last_json(cxx_proc.stdout)
        require(cxx_payload.get("hata_sayisi") == 0, "C++ lexer reported errors")
        cxx_tokens = cxx_payload.get("tokenlar")
        require(isinstance(cxx_tokens, list), "C++ lexer JSON missing tokenlar list")

        source_path = source_file.resolve().as_posix()
        driver_file.write_text(
            'lexer olsun dahil_et "orhun/lexer.oh"\n'
            f'kaynak olsun dosya.oku("{orhun_string(source_path)}")\n'
            "tokenlar olsun lexer.tokenlestir(kaynak)\n"
            "yazdır json.yaz(tokenlar)\n",
            encoding="utf-8",
            newline="\n",
        )

        orhun_proc = run_cmd([str(binary), str(driver_file)], repo)
        require(
            orhun_proc.returncode == 0,
            f"Orhun lexer driver failed:\nSTDOUT:\n{orhun_proc.stdout}\nSTDERR:\n{orhun_proc.stderr}",
        )
        orhun_tokens = parse_last_json(orhun_proc.stdout)
        require(isinstance(orhun_tokens, list), "Orhun lexer output is not a list")

        left = normalized(cxx_tokens, include_position)
        right = normalized(orhun_tokens, include_position)
        require(
            left == right,
            "Lexer parity mismatch\n"
            f"C++:   {json.dumps(left, ensure_ascii=False)}\n"
            f"Orhun: {json.dumps(right, ensure_ascii=False)}",
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="C++ lexer / Orhun lexer parity smoke")
    parser.add_argument("binary", help="Orhun executable path")
    args = parser.parse_args()

    binary = Path(args.binary).resolve()
    if not binary.exists():
        raise SystemExit(f"Binary not found: {binary}")

    repo = Path.cwd()

    compare_case(
        binary,
        repo,
        "blok:\n"
        "    x olsun 1\n"
        "    y olsun 10.5\n"
        "    yaz \"metin\"\n",
        include_position=True,
    )

    compare_case(
        binary,
        repo,
        "işlev ana():\n"
        "    yazdır \"Merhaba\"\n",
        include_position=False,
    )

    print("Lexer parity smoke passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
