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

    stdlib_dil = (repo / "examples" / "stdlib_dil.oh").read_text(
        encoding="utf-8"
    )
    for snippet in (
        "dil.token_degerleri(tokenlar)",
        "dil.hata_var_mi(imlec)",
        "dil.tani_mesajlari(hatalar)",
        "dil.tani_listesi_bicimlendir(hatalar.hatalar)",
        "dil.tani_listesi_ozeti(hatalar.hatalar)",
        "dil.dugum_turlerini_duzlestir(ast)",
        'dil.dugum_turu_var_mi(ast, "SelamKomutu")',
        "dil.dugum_ozeti(ast)",
    ):
        require(snippet in stdlib_dil, f"stdlib_dil should include {snippet}")

    stdlib_lexer = (repo / "examples" / "stdlib_lexer.oh").read_text(
        encoding="utf-8"
    )
    require(
        "lexer.token_araligi(tokenlar[0])" in stdlib_lexer,
        "stdlib_lexer should expose token ranges",
    )

    stdlib_parser = (repo / "examples" / "stdlib_parser.oh").read_text(
        encoding="utf-8"
    )
    for snippet in (
        "parser.komut_satir_araligi(sonuc.komutlar[0])",
        "parser.ifade_satir_araligi(sonuc.komutlar[0].ifade_ozeti)",
        "parser.tum_ifade_satir_araliklari(sonuc)",
        "parser.ifade_agaci_ozeti(sonuc)",
        "parser.tum_komut_satir_araliklari(sonuc)",
        "parser.komut_agaci_ozeti(sonuc)",
        "parser.ir_ozeti(sonuc)",
        "parser.hata_tanilari(hatali)",
    ):
        require(snippet in stdlib_parser, f"stdlib_parser should include {snippet}")

    print(f"Examples smoke passed ({len(examples)} examples).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
