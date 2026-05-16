#!/usr/bin/env python3
import argparse
import json
import subprocess
import tempfile
from pathlib import Path


DEFAULT_FIXTURE_DIR = Path("tests/ast_json")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def parse_last_json(text: str) -> dict:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    require(lines, "JSON output is empty")
    return json.loads(lines[-1])


def run_cmd(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=cwd,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def fixture_metadata(path: Path) -> tuple[bool, list[str] | None]:
    try:
        first_line = path.read_text(encoding="utf-8").splitlines()[0].strip()
    except IndexError:
        return False, None

    if first_line == "# ast-error":
        return True, None
    if first_line.startswith("# ast:"):
        raw = first_line.removeprefix("# ast:").strip()
        expected = [item.strip() for item in raw.split(",") if item.strip()]
        return False, expected
    return False, None


def validate_success_payload(
    payload: dict, expected_kinds: list[str] | None, path: Path
) -> None:
    require(
        payload.get("durum") == "ok",
        f"{path}: success payload durum must be ok",
    )
    require(
        payload.get("hata_sayisi") == 0,
        f"{path}: success payload must have no errors",
    )
    ast = payload.get("ast")
    require(isinstance(ast, dict), f"{path}: success payload missing ast object")
    require(ast.get("tur") == "Program", f"{path}: root AST node must be Program")
    komutlar = ast.get("komutlar")
    require(isinstance(komutlar, list), f"{path}: Program node missing komutlar")

    if expected_kinds is not None:
        actual = [komut.get("tur") for komut in komutlar]
        require(
            actual == expected_kinds,
            f"{path}: top-level AST kinds changed\n"
            f"expected={expected_kinds}\nactual={actual}",
        )


def validate_error_payload(payload: dict, path: Path) -> None:
    require(
        payload.get("durum") == "fail",
        f"{path}: error payload durum must be fail",
    )
    require(
        payload.get("hata_sayisi") == 1,
        f"{path}: error payload must report one error",
    )
    require(payload.get("ast") is None, f"{path}: error payload ast must be null")
    require(
        isinstance(payload.get("hata", {}).get("mesaj"), str)
        and payload["hata"]["mesaj"],
        f"{path}: error payload missing hata.mesaj",
    )


def compare_file(
    binary: Path, repo: Path, source_file: Path, run_tree: bool
) -> tuple[int, int]:
    should_fail, expected_kinds = fixture_metadata(source_file)
    proc = run_cmd([str(binary), "parse", str(source_file), "--json"], repo)

    if should_fail:
        require(
            proc.returncode == 1,
            f"{source_file}: parse --json should return rc=1 on parser errors",
        )
        validate_error_payload(parse_last_json(proc.stdout), source_file)
        return 0, 1

    require(
        proc.returncode == 0,
        f"{source_file}: parse --json failed:\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}",
    )
    validate_success_payload(
        parse_last_json(proc.stdout), expected_kinds, source_file
    )

    if run_tree:
        tree_proc = run_cmd([str(binary), "ast", str(source_file)], repo)
        require(
            tree_proc.returncode == 0,
            f"{source_file}: ast command should print tree",
        )
        require(
            "ProgramNode" in tree_proc.stdout,
            f"{source_file}: tree output missing ProgramNode",
        )

    return 1, 0


def compare_inline_cases(binary: Path, repo: Path) -> tuple[int, int]:
    with tempfile.TemporaryDirectory(prefix="orhun_ast_json_") as tmp:
        tmpdir = Path(tmp)
        ok_source = tmpdir / "ast_ok.oh"
        ok_source.write_text(
            "\n".join(
                [
                    "# ast: IslevTanim,Atama,Yazdir",
                    "işlev topla(a olsun 1, b olsun 2):",
                    "    döndür a + b",
                    "",
                    "sonuç olsun topla(3)",
                    "yazdır sonuç",
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )

        bad_source = tmpdir / "ast_bad.oh"
        bad_source.write_text(
            "# ast-error\neğer doğru\n", encoding="utf-8", newline="\n"
        )

        ok_count, err_count = compare_file(binary, repo, ok_source, run_tree=True)
        more_ok, more_err = compare_file(binary, repo, bad_source, run_tree=False)
        return ok_count + more_ok, err_count + more_err


def main() -> int:
    parser = argparse.ArgumentParser(description="Orhun parse --json smoke test")
    parser.add_argument("binary", help="Orhun executable path")
    parser.add_argument(
        "--fixtures",
        default=str(DEFAULT_FIXTURE_DIR),
        help="Directory containing parser AST JSON .oh fixtures",
    )
    args = parser.parse_args()

    repo = Path(__file__).resolve().parents[1]
    binary = Path(args.binary).resolve()
    if not binary.exists():
        raise SystemExit(f"Binary not found: {binary}")

    fixture_dir = (repo / args.fixtures).resolve()
    cases = sorted(fixture_dir.glob("*.oh")) if fixture_dir.exists() else []

    if not cases:
        ok_count, err_count = compare_inline_cases(binary, repo)
        print(
            f"AST JSON smoke passed ({ok_count} inline ok, "
            f"{err_count} inline error)."
        )
        return 0

    ok_count = 0
    err_count = 0
    tree_checked = False
    for case in cases:
        ok, err = compare_file(binary, repo, case, run_tree=not tree_checked)
        ok_count += ok
        err_count += err
        if ok:
            tree_checked = True

    print(f"AST JSON smoke passed ({ok_count} fixture ok, {err_count} fixture error).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
