#!/usr/bin/env python3
import argparse
import json
import subprocess
import tempfile
from pathlib import Path


def run_cmd(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def parse_last_json(text: str) -> dict:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        raise RuntimeError("json output is empty")
    return json.loads(lines[-1])


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> int:
    parser = argparse.ArgumentParser(description="Orhun fmt/lint DX smoke test")
    parser.add_argument("binary", help="Orhun executable path")
    args = parser.parse_args()

    binary = Path(args.binary)
    if not binary.exists():
        raise SystemExit(f"Binary not found: {binary}")

    with tempfile.TemporaryDirectory(prefix="orhun_dx_smoke_") as tmp:
        root = Path(tmp)

        fmt_file = root / "fmt_case.oh"
        fmt_file.write_text("islev topla(a,b):\n    dondur a+b\n", encoding="utf-8")

        fmt_check_fail = run_cmd(
            [str(binary), "fmt", str(fmt_file), "--check", "--json"]
        )
        require(
            fmt_check_fail.returncode == 1,
            f"fmt --check should fail before formatting: {fmt_check_fail.stdout}\n{fmt_check_fail.stderr}",
        )
        fmt_check_payload = parse_last_json(fmt_check_fail.stdout)
        require(
            fmt_check_payload.get("durum") == "needs_format",
            "fmt check JSON should report needs_format",
        )

        fmt_write = run_cmd([str(binary), "fmt", str(fmt_file), "--json"])
        require(
            fmt_write.returncode == 0,
            f"fmt write should pass: {fmt_write.stdout}\n{fmt_write.stderr}",
        )
        fmt_write_payload = parse_last_json(fmt_write.stdout)
        require(
            fmt_write_payload.get("durum") in ("formatted", "unchanged"),
            "fmt write JSON should report formatted/unchanged",
        )

        fmt_check_ok = run_cmd([str(binary), "fmt", str(fmt_file), "--check", "--json"])
        require(
            fmt_check_ok.returncode == 0,
            f"fmt --check should pass after formatting: {fmt_check_ok.stdout}\n{fmt_check_ok.stderr}",
        )
        fmt_check_ok_payload = parse_last_json(fmt_check_ok.stdout)
        require(fmt_check_ok_payload.get("durum") == "ok", "fmt check should be ok")

        lint_warn = root / "lint_warn.oh"
        lint_warn.write_text(
            "metin olsun \"" + ("a" * 180) + "\"\n",
            encoding="utf-8",
        )

        lint_warn_proc = run_cmd([str(binary), "lint", str(lint_warn), "--json"])
        require(
            lint_warn_proc.returncode == 0,
            f"lint non-strict should pass with warnings: {lint_warn_proc.stdout}\n{lint_warn_proc.stderr}",
        )
        lint_warn_payload = parse_last_json(lint_warn_proc.stdout)
        require(
            lint_warn_payload.get("uyari_sayisi", 0) > 0,
            "lint warning file should produce warning count",
        )
        require(
            lint_warn_payload.get("durum") == "ok",
            "lint non-strict should report ok",
        )

        lint_strict_proc = run_cmd(
            [str(binary), "lint", str(lint_warn), "--strict", "--json"]
        )
        require(
            lint_strict_proc.returncode == 1,
            "lint strict should fail when warnings exist",
        )
        lint_strict_payload = parse_last_json(lint_strict_proc.stdout)
        require(
            lint_strict_payload.get("durum") == "fail",
            "lint strict should report fail",
        )

        lint_err = root / "lint_err.oh"
        lint_err.write_text("islev bozuk(a, b olsun ):\n    dondur a\n", encoding="utf-8")

        lint_err_proc = run_cmd([str(binary), "lint", str(lint_err), "--json"])
        require(
            lint_err_proc.returncode == 1,
            "lint should fail on parser error",
        )
        lint_err_payload = parse_last_json(lint_err_proc.stdout)
        require(
            lint_err_payload.get("hata_sayisi", 0) > 0,
            "lint parser error case should report errors",
        )

    print("DX fmt/lint smoke passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
