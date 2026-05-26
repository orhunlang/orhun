#!/usr/bin/env python3
import argparse
from pathlib import Path

from capture_analysis_common import analyze_file, require


def main() -> int:
    parser = argparse.ArgumentParser(description="Static closure capture analysis smoke")
    parser.add_argument("binary", help="Orhun executable")
    args = parser.parse_args()

    repo = Path.cwd()
    binary = Path(args.binary)
    require(binary.exists(), f"Binary not found: {binary}")

    source = repo / "tests" / "cases" / "closure_missing_feature.oh"
    require(source.exists(), f"Closure capture fixture not found: {source}")
    results = analyze_file(binary, repo, source)

    expected = {
        "<program>.sayac_uret.artir": ({"adet"}, {"adet"}),
        "<program>.dis_fonksiyon.ic_fonksiyon": ({"dis_x", "param"}, set()),
        "<program>.banka_hesabi.para_yatir": ({"bakiye"}, {"bakiye"}),
        "<program>.banka_hesabi.para_cek": ({"bakiye"}, {"bakiye"}),
        "<program>.fonksiyon_listesi_uret.yazdir_func": ({"x"}, set()),
    }

    for path, (captures, mutated_captures) in expected.items():
        require(path in results, f"Closure analysis missing function path: {path}")
        require(
            results[path].captures == captures,
            f"{path} captures changed: expected={sorted(captures)} "
            f"actual={sorted(results[path].captures)} refs={sorted(results[path].refs)} "
            f"locals={sorted(results[path].locals)}",
        )
        require(
            results[path].mutated_captures == mutated_captures,
            f"{path} mutated captures changed: expected={sorted(mutated_captures)} "
            f"actual={sorted(results[path].mutated_captures)} "
            f"writes={sorted(results[path].writes)}",
        )

    print(f"Closure capture analysis smoke passed ({len(expected)} closures).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
