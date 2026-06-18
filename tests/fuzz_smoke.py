#!/usr/bin/env python3
import argparse
import random
import subprocess
import tempfile
from pathlib import Path


IDS = [
    "a",
    "b",
    "x",
    "y",
    "sayac",
    "veri",
    "deger",
    "isim",
    "liste",
]
TEXTS = ['"orhun"', '"test"', '"abc"', '"42"']
OPS = ["+", "-", "*", "/"]
CMPS = ["eşit", "büyük", "küçük"]


def rand_literal() -> str:
    r = random.random()
    if r < 0.35:
        return str(random.randint(-50, 200))
    if r < 0.65:
        return f"{random.randint(0, 20)}.{random.randint(0, 99)}"
    if r < 0.85:
        return random.choice(TEXTS)
    return random.choice(IDS)


def rand_expr(depth: int = 0) -> str:
    if depth > 2 or random.random() < 0.45:
        return rand_literal()
    left = rand_expr(depth + 1)
    right = rand_expr(depth + 1)
    op = random.choice(OPS)
    return f"{left} {op} {right}"


def rand_basic_line() -> str:
    r = random.random()
    if r < 0.25:
        return f"{random.choice(IDS)} olsun {rand_expr()}"
    if r < 0.50:
        return f"{random.choice(IDS)} = {rand_expr()}"
    if r < 0.65:
        return f"yazdır {rand_expr()}"
    if r < 0.80:
        return f"eğer {rand_expr()} eşit {rand_expr()} ise: yazdır {rand_expr()}"
    if r < 0.88:
        return f"tekrarla {random.randint(0, 5)} kez yazdır {rand_expr()}"
    if r < 0.96:
        return f"her {random.choice(IDS)} içinde [1, 2, 3]: yazdır {rand_expr()}"
    # Bilinçli bozuk satır: çökme olmamalı, hata mesajı üretmeli.
    return f"{random.choice(IDS)} olsun"


def rand_advanced_line() -> str:
    r = random.random()
    if r < 0.15:
        return f"{random.choice(IDS)}, {random.choice(IDS)} olsun [1, 2]"
    if r < 0.30:
        return f"{random.choice(IDS)} olsun işlev(x olsun {random.randint(1, 5)}): x + {random.randint(1, 9)}"
    if r < 0.45:
        return (
            f"işlev f_{random.randint(0, 30)}(a, b olsun {random.randint(1, 6)}):"
            f" döndür a + b"
        )
    if r < 0.60:
        return (
            f"eğer {rand_expr()} {random.choice(CMPS)} {rand_expr()} ise:"
            f" yazdır {rand_expr()}"
        )
    if r < 0.70:
        return f"deneme: yazdır {rand_expr()} yakala e: yazdır e"
    if r < 0.80:
        return f"yazdır json.yaz({rand_expr()})"
    if r < 0.88:
        item = random.choice(IDS)
        return f"yazdır [{item} * {item} için {item} içinde [1, 2, 3]]"
    if r < 0.96:
        return f"her {random.choice(IDS)} içinde [1, 2, 3]: yazdır {rand_expr()}"
    if r < 0.98:
        return f"yazdır regex.eslesir(\"abc123\", \"[a-z]+\")"
    return rand_basic_line()


def rand_template_program() -> str:
    secim = random.randint(0, 6)
    if secim == 0:
        return (
            "tip Kutu:\n"
            "    işlev kur(x olsun 2):\n"
            "        benim.x olsun x\n"
            "    işlev carp(y olsun 3):\n"
            "        döndür benim.x * y\n"
            "k olsun yeni Kutu()\n"
            "yazdır k.carp()\n"
        )
    if secim == 1:
        return (
            "işlev topla(a, b olsun 10):\n"
            "    döndür a + b\n"
            "f olsun işlev(x olsun 5): x * 2\n"
            "yazdır topla(f())\n"
        )
    if secim == 2:
        return (
            "a, b, c olsun [1, 2, 3]\n"
            "işlev g(x):\n"
            "    döndür x + a\n"
            "yazdır g(b)\n"
            "yazdır c\n"
        )
    if secim == 3:
        return (
            "deneme:\n"
            "    l olsun [1]\n"
            "    yazdır l[2]\n"
            "yakala e:\n"
            "    yazdır e\n"
        )
    if secim == 4:
        return (
            "v olsun {\"ad\": \"orhun\", \"sayi\": 7}\n"
            "yazdır json.guzel_yaz(v)\n"
            "yazdır metin.uzunluk(\"abc\")\n"
        )
    if secim == 5:
        return (
            "sayilar olsun [1, 2, 3, 4]\n"
            "toplam olsun 0\n"
            "her sayi içinde sayilar:\n"
            "    toplam olsun toplam + sayi\n"
            "yazdır toplam\n"
            "yazdır [x * x için x içinde sayilar eğer x büyük 2]\n"
        )
    return (
        "işlev dene(k olsun 3):\n"
        "    tekrarla k kez yazdır k\n"
        "dene(2)\n"
        "yazdır veritabani.oku(\"olmayan\")\n"
    )


def rand_program(lines: int, profile: str) -> str:
    if profile == "advanced" and random.random() < 0.55:
        return rand_template_program()

    out = []
    for _ in range(lines):
        if profile == "advanced":
            out.append(rand_advanced_line())
        else:
            out.append(rand_basic_line())
    return "\n".join(out) + "\n"


def is_crash(returncode: int, stderr: str) -> bool:
    crash_codes = {134, 136, 139, -11, -6, 3221225477, 3221226505}
    if returncode in crash_codes:
        return True
    low = stderr.lower()
    return "segmentation fault" in low or "access violation" in low


def main() -> int:
    parser = argparse.ArgumentParser(description="Orhun lexer/parser/interpreter fuzz smoke")
    parser.add_argument("binary", nargs="?", default="orhun_test", help="Orhun executable path")
    parser.add_argument("--count", type=int, default=120, help="Fuzz iteration count")
    parser.add_argument("--seed", type=int, default=1337, help="Deterministic random seed")
    parser.add_argument("--timeout", type=float, default=2.0, help="Timeout per run (seconds)")
    parser.add_argument(
        "--profile",
        choices=("basic", "advanced"),
        default="advanced",
        help="Fuzz profile",
    )
    parser.add_argument(
        "--vm-strict",
        action="store_true",
        help="Run each fuzz case with `vm-kati` mode",
    )
    args = parser.parse_args()

    random.seed(args.seed)
    binary = Path(args.binary)
    if not binary.exists():
        raise SystemExit(f"Binary not found: {binary}")

    with tempfile.TemporaryDirectory(prefix="orhun_fuzz_") as td:
        base = Path(td)
        for i in range(args.count):
            src = base / f"fuzz_{i}.oh"
            src.write_text(
                rand_program(random.randint(1, 24), args.profile),
                encoding="utf-8",
            )
            cmd = [str(binary), str(src)]
            if args.vm_strict:
                cmd = [str(binary), "vm-kati", str(src)]
            try:
                proc = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=args.timeout,
                    check=False,
                )
            except subprocess.TimeoutExpired:
                print(f"[FAIL] timeout at iteration {i}")
                print(src.read_text(encoding="utf-8"))
                return 1

            if is_crash(proc.returncode, proc.stderr):
                print(f"[FAIL] crash at iteration {i}, return={proc.returncode}")
                print(src.read_text(encoding="utf-8"))
                print(proc.stderr)
                return 1

            if (i + 1) % 20 == 0:
                print(f"[OK] {i + 1}/{args.count}")

    print("Fuzz smoke completed without crash.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
