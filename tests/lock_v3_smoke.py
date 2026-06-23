#!/usr/bin/env python3
import argparse
import subprocess
import tempfile
from pathlib import Path


def run_cmd(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=str(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> int:
    parser = argparse.ArgumentParser(description="Orhun lock v3 smoke test")
    parser.add_argument("binary", help="Orhun executable")
    args = parser.parse_args()

    binary = Path(args.binary).resolve()
    if not binary.exists():
        raise SystemExit(f"Binary not found: {binary}")

    with tempfile.TemporaryDirectory(prefix="orhun_lock_v3_") as tmp:
        root = Path(tmp)
        kaynak = root / "kaynak_paket"
        kaynak.mkdir(parents=True, exist_ok=True)
        (kaynak / "modul.oh").write_text("yazdir 1\n", encoding="utf-8")

        kur = run_cmd([str(binary), "paket", "kur", str(kaynak), "deneme_paket"], root)
        require(kur.returncode == 0, f"paket kur failed: {kur.stdout}\n{kur.stderr}")

        lock = root / "orhun.lock"
        require(lock.exists(), "orhun.lock was not created")
        lock_text = lock.read_text(encoding="utf-8")
        require("|v3|" in lock_text, "lock file is not in v3 format")

        dogrula_ok = run_cmd([str(binary), "paket", "dogrula"], root)
        require(
            dogrula_ok.returncode == 0,
            f"paket dogrula should pass after install: {dogrula_ok.stdout}\n{dogrula_ok.stderr}",
        )

        hedef_modul = root / "lib" / "deneme_paket" / "modul.oh"
        hedef_modul.write_text("yazdir 2\n", encoding="utf-8")

        dogrula_fail = run_cmd([str(binary), "paket", "dogrula"], root)
        fail_text = (dogrula_fail.stdout + dogrula_fail.stderr).lower()
        require(dogrula_fail.returncode != 0, "paket dogrula should fail after package tamper")
        require("icerik hash" in fail_text, "tamper failure should mention content hash")

        lock_guncelle = run_cmd([str(binary), "paket", "lock-guncelle"], root)
        require(
            lock_guncelle.returncode == 0,
            f"paket lock-guncelle failed: {lock_guncelle.stdout}\n{lock_guncelle.stderr}",
        )

        dogrula_tekrar = run_cmd([str(binary), "paket", "dogrula"], root)
        require(
            dogrula_tekrar.returncode == 0,
            f"paket dogrula should pass after lock update: {dogrula_tekrar.stdout}\n{dogrula_tekrar.stderr}",
        )

        lock_text = lock.read_text(encoding="utf-8")
        lock.write_text(lock_text + "\n" + lock_text, encoding="utf-8")
        for command in ("dogrula", "lock-guncelle"):
            tekrarli = run_cmd([str(binary), "paket", command], root)
            tekrarli_text = (tekrarli.stdout + tekrarli.stderr).lower()
            require(tekrarli.returncode != 0, f"duplicate lock entry passed {command}")
            require(
                "tekrar eden paket" in tekrarli_text,
                f"duplicate lock rejection should explain the package ({command})",
            )

        lock.write_text(
            "# ad|kaynak|sha256|surum|commit_pin|icerik_sha256|source_ref\n"
            "..|kaynak|gecersiz|v3|-|gecersiz|\n",
            encoding="utf-8",
        )
        for command in ("dogrula", "lock-guncelle"):
            rejected = run_cmd([str(binary), "paket", command], root)
            rejected_text = (rejected.stdout + rejected.stderr).lower()
            require(rejected.returncode != 0, f"unsafe lock name passed {command}")
            require(
                "paket adi gecersiz" in rejected_text,
                f"unsafe lock rejection should explain package name ({command})",
            )

    print("Lock v3 smoke passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
