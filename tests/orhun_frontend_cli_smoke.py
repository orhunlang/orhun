#!/usr/bin/env python3
import argparse
import json
import subprocess
import tempfile
from pathlib import Path


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def run(binary: Path, repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(binary), *args],
        cwd=repo,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def payload(proc: subprocess.CompletedProcess[str], context: str) -> dict:
    lines = [line for line in proc.stdout.splitlines() if line.strip()]
    require(lines, f"{context}: JSON output is empty")
    value = json.loads(lines[-1])
    require(isinstance(value, dict), f"{context}: JSON output must be an object")
    return value


def normalized_tokens(value: dict) -> list[tuple[object, ...]]:
    tokens = value.get("tokenlar")
    require(isinstance(tokens, list), "token list is missing")
    return [
        (
            token.get("tur"),
            token.get("deger"),
            token.get("satir"),
            token.get("sutun"),
        )
        for token in tokens
    ]


def validation_ok(value: dict, contract: str, context: str) -> None:
    require(value.get("ir_sozlesmesi") == contract, f"{context}: contract mismatch")
    validation = value.get("ir_dogrulamasi")
    require(isinstance(validation, dict), f"{context}: validation is missing")
    require(validation.get("ok") is True, f"{context}: validation failed")
    require(validation.get("sozlesme") == contract, f"{context}: validation contract mismatch")


def parser_provenance_ok(value: dict, context: str) -> None:
    require(
        value.get("lexer_ir_sozlesmesi") == "orhun-lexer-ir-v1",
        f"{context}: lexer provenance contract mismatch",
    )
    require(value.get("lexer_ir_gecerli") is True, f"{context}: lexer provenance is invalid")


def main() -> int:
    parser = argparse.ArgumentParser(description="Orhun-written frontend CLI smoke")
    parser.add_argument("binary", help="Orhun executable path")
    args = parser.parse_args()

    repo = Path(__file__).resolve().parents[1]
    binary = Path(args.binary).resolve()
    require(binary.exists(), f"Binary not found: {binary}")

    with tempfile.TemporaryDirectory(prefix="orhun_frontend_cli_") as tmp:
        root = Path(tmp)
        valid = root / "valid.oh"
        parser_error = root / "parser_error.oh"
        lexer_error = root / "lexer_error.oh"
        wrong_extension = root / "valid.txt"
        valid.write_text('deger olsun 2\nyaz deger + 3\n', encoding="utf-8")
        parser_error.write_text("yzdır 1\n", encoding="utf-8")
        lexer_error.write_text("@\n", encoding="utf-8")
        wrong_extension.write_text("yaz 1\n", encoding="utf-8")

        cxx_lex = run(binary, repo, "lex", str(valid), "--json")
        pure_lex = run(binary, repo, "orhun-lex", str(valid), "--source")
        require(cxx_lex.returncode == 0, f"C++ lex failed: {cxx_lex.stderr}")
        require(pure_lex.returncode == 0, f"orhun-lex failed: {pure_lex.stderr}")
        cxx_lex_value = payload(cxx_lex, "C++ lex")
        pure_lex_value = payload(pure_lex, "orhun-lex")
        validation_ok(pure_lex_value, "orhun-lexer-ir-v1", "orhun-lex")
        require(
            normalized_tokens(pure_lex_value) == normalized_tokens(cxx_lex_value),
            "orhun-lex token stream differs from C++ lex",
        )

        pure_parse = run(binary, repo, "orhun-parse", str(valid), "--source")
        require(pure_parse.returncode == 0, f"orhun-parse failed: {pure_parse.stderr}")
        pure_parse_value = payload(pure_parse, "orhun-parse")
        validation_ok(pure_parse_value, "orhun-parser-ir-v2", "orhun-parse")
        parser_provenance_ok(pure_parse_value, "orhun-parse")
        require(pure_parse_value.get("ok") is True, "orhun-parse should accept valid source")
        require(pure_parse_value.get("tur") == "Program", "orhun-parse root kind mismatch")
        require(pure_parse_value.get("komut_sayisi") == 2, "orhun-parse command count mismatch")

        obc_first_parse = run(binary, repo, "orhun-parse", str(valid), "--obc-first")
        require(
            obc_first_parse.returncode == 0,
            f"orhun-parse --obc-first failed: {obc_first_parse.stderr}",
        )
        validation_ok(
            payload(obc_first_parse, "orhun-parse --obc-first"),
            "orhun-parser-ir-v2",
            "orhun-parse --obc-first",
        )

        parser_failure = run(binary, repo, "orhun-parse", str(parser_error))
        require(parser_failure.returncode == 1, "orhun-parse should reject parser errors")
        parser_failure_value = payload(parser_failure, "orhun-parse parser error")
        validation_ok(
            parser_failure_value,
            "orhun-parser-ir-v2",
            "orhun-parse parser error",
        )
        parser_provenance_ok(parser_failure_value, "orhun-parse parser error")
        require(parser_failure_value.get("ok") is False, "parser error should set ok=false")
        require(
            "yazdır" in json.dumps(parser_failure_value, ensure_ascii=False),
            "parser error should retain the Turkish command suggestion",
        )

        lexer_failure = run(binary, repo, "orhun-lex", str(lexer_error))
        require(lexer_failure.returncode == 1, "orhun-lex should reject lexer errors")
        lexer_failure_value = payload(lexer_failure, "orhun-lex lexer error")
        validation_ok(
            lexer_failure_value,
            "orhun-lexer-ir-v1",
            "orhun-lex lexer error",
        )
        require(lexer_failure_value.get("hata_sayisi") == 1, "lexer error count mismatch")

        parser_lexer_failure = run(binary, repo, "orhun-parse", str(lexer_error))
        require(
            parser_lexer_failure.returncode == 1,
            "orhun-parse should reject lexer errors",
        )
        parser_lexer_value = payload(parser_lexer_failure, "orhun-parse lexer error")
        validation_ok(
            parser_lexer_value,
            "orhun-parser-ir-v2",
            "orhun-parse lexer error",
        )
        parser_provenance_ok(parser_lexer_value, "orhun-parse lexer error")
        require(parser_lexer_value.get("ok") is False, "lexer error should set parser ok=false")

        bad_option = run(binary, repo, "orhun-parse", str(valid), "--unknown")
        require(bad_option.returncode != 0, "orhun-parse should reject unknown options")
        require("bilinmeyen orhun-parse" in bad_option.stderr, "unknown option error mismatch")

        duplicate_mode = run(
            binary,
            repo,
            "orhun-lex",
            str(valid),
            "--source",
            "--obc-first",
        )
        require(duplicate_mode.returncode != 0, "orhun-lex should reject duplicate modes")

        wrong_file = run(binary, repo, "orhun-lex", str(wrong_extension))
        require(wrong_file.returncode != 0, "orhun-lex should reject non-.oh files")
        require(".oh dosyasi" in wrong_file.stderr, "wrong-extension error mismatch")

    print("Orhun frontend CLI smoke passed (lexer/parser success and error paths).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
