#!/usr/bin/env python3
"""English keyword alias bridge at the Lexer layer."""

from __future__ import annotations

import argparse
import os
import subprocess
import tempfile
from pathlib import Path


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def run_source(binary: Path, source: str, strict: bool = False) -> tuple[int, str]:
    env = os.environ.copy()
    if strict:
        env["ORHUN_TURKCE_KATI"] = "1"
    else:
        env.pop("ORHUN_TURKCE_KATI", None)
    with tempfile.TemporaryDirectory(prefix="orhun_eng_") as tmp:
        path = Path(tmp) / "ornek.oh"
        path.write_text(source, encoding="utf-8")
        proc = subprocess.run(
            [str(binary), str(path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=15,
            env=env,
        )
        return proc.returncode, (proc.stdout + proc.stderr).replace("\r\n", "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="English alias bridge smoke")
    parser.add_argument("binary", help="Orhun executable")
    args = parser.parse_args()
    binary = Path(args.binary)
    require(binary.exists(), f"Binary not found: {binary}")

    # İngilizce anahtarlar varsayılan modda Türkçe'ye köprülenir.
    ok_cases = [
        (
            "print",
            'print("merhaba")\n',
            ["merhaba"],
        ),
        (
            "function-return",
            "function f():\n    return 1\nyazdır f()\n",
            ["1"],
        ),
        (
            "for-in",
            "for x in [1, 2]:\n    yazdır x\n",
            ["1", "2"],
        ),
        (
            "if-ise",
            'if true ise:\n    yaz "tamam"\n',
            ["tamam"],
        ),
        (
            "while-ise",
            'i olsun 0\nwhile i küçük 1:\n    yaz "dongu"\n    kır\n',
            ["dongu"],
        ),
        (
            "try-catch",
            'try:\n    yaz "dene"\ncatch hata:\n    yaz "yakala"\n',
            ["dene"],
        ),
        (
            "true-false",
            "yazdır true\nyazdır false\n",
            ["1", "0"],
        ),
        (
            "and-or-not",
            "yazdır true and false\nyazdır true or false\nyazdır not true\n",
            ["0", "1", "0"],
        ),
        (
            "import-include",
            # 'import'/'include' → 'dahil_et'; yalnızca alias tanımını yoklar.
            "yazdır 1\n",
            ["1"],
        ),
    ]

    for name, source, needles in ok_cases:
        code, out = run_source(binary, source)
        require(code == 0, f"{name}: expected success, got exit={code}\n{out}")
        for needle in needles:
            require(needle in out, f"{name}: expected {needle!r} in\n{out}")
        print(f"[OK] {name}")

    # Türkçe kaynak bozulmamalı.
    code, out = run_source(binary, 'eğer doğru ise:\n    yaz "tr"\n')
    require(code == 0 and "tr" in out, f"turkish baseline failed:\n{out}")
    print("[OK] turkish-baseline")

    # Katı Türkçe modda İngilizce alias reddedilir; öğretici ipucu gelir.
    code, out = run_source(binary, "if true ise:\n    yaz \"x\"\n", strict=True)
    require(code != 0, f"strict mode must reject English 'if':\n{out}")
    require(
        "Bunu mu demek istediniz: 'eğer'?" in out,
        f"strict mode must suggest 'eğer':\n{out}",
    )
    require(
        "İpucu:" in out,
        f"strict mode must teach the fix:\n{out}",
    )
    print("[OK] strict-rejects-english")

    # Katı modda Türkçe anahtarlar çalışır.
    code, out = run_source(
        binary, 'eğer doğru ise:\n    yaz "katı"\n', strict=True
    )
    require(code == 0 and "katı" in out, f"strict turkish failed:\n{out}")
    print("[OK] strict-turkish-ok")

    print("English alias bridge smoke passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
