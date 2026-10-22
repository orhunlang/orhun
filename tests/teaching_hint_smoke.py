#!/usr/bin/env python3
"""Compiler-as-a-Teacher smoke: Turkish fix hints on common beginner errors."""

from __future__ import annotations

import argparse
import subprocess
import tempfile
from pathlib import Path


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def run_source(binary: Path, source: str) -> str:
    with tempfile.TemporaryDirectory(prefix="orhun_teacher_") as tmp:
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
        )
        return (proc.stdout + proc.stderr).replace("\r\n", "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Teaching-hint smoke")
    parser.add_argument("binary", help="Orhun executable")
    args = parser.parse_args()
    binary = Path(args.binary)
    require(binary.exists(), f"Binary not found: {binary}")

    cases = [
        (
            "eksik-iki-nokta-islev",
            "işlev topla(a, b)\n    döndür a + b\n",
            [
                "İşlev başlığından sonra ':'",
                "İpucu: İşlev tanımı iki nokta ile biter.",
                "Örnek: işlev topla(a, b):",
            ],
        ),
        (
            "eksik-ise",
            "eğer doğru\n    yaz \"x\"\n",
            [
                "Koşuldan sonra 'ise' bekleniyor.",
                "İpucu: Koşuldan sonra 'ise' ve iki nokta gelir.",
                "Örnek: eğer dogru ise:",
            ],
        ),
        (
            "ingilizce-if",
            "if true\n    yaz \"x\"\n",
            [
                "Bunu mu demek istediniz: 'eğer'?",
                "İpucu: Orhun Türkçe sözdizimi kullanır; 'if' yerine 'eğer' yazın.",
            ],
        ),
        (
            "ingilizce-function",
            "function f():\n    döndür 1\n",
            [
                "Bunu mu demek istediniz: 'işlev'?",
                "İpucu: Orhun Türkçe sözdizimi kullanır; 'function' yerine 'işlev' yazın.",
            ],
        ),
        (
            "ingilizce-return",
            "işlev f():\n    return 1\n",
            [
                "Bunu mu demek istediniz: 'döndür'?",
                "İpucu: Orhun Türkçe sözdizimi kullanır; 'return' yerine 'döndür' yazın.",
            ],
        ),
        (
            "ingilizce-print",
            "print(\"merhaba\")\n",
            [
                "Bunu mu demek istediniz: 'yazdır'?",
                "İpucu: Orhun Türkçe sözdizimi kullanır; 'print' yerine 'yazdır' yazın.",
            ],
        ),
        (
            "tanimsiz-degisken",
            "yazdır tanimli_degil\n",
            [
                "Tanımsız değişken: 'tanimli_degil'.",
                "İpucu: Değişkeni 'ad olsun deger' ile tanımlayın",
                "Örnek: sayi olsun 0",
            ],
        ),
    ]

    for name, source, needles in cases:
        out = run_source(binary, source)
        for needle in needles:
            require(
                needle in out,
                f"{name}: expected {needle!r} in output:\n{out}",
            )
        print(f"[OK] {name}")

    # İngilizce 'if' artık 'ise'ye kaymamalı.
    out = run_source(binary, "if true\n    yaz \"x\"\n")
    require(
        "Bunu mu demek istediniz: 'ise'?" not in out,
        "English 'if' must not suggest 'ise'",
    )
    print("[OK] if-not-ise")

    print("Teaching-hint smoke passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
