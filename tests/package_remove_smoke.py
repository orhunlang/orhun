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
    parser = argparse.ArgumentParser(description="Safe package removal smoke test")
    parser.add_argument("binary", help="Orhun executable")
    args = parser.parse_args()

    binary = Path(args.binary).resolve()
    require(binary.is_file(), f"Binary not found: {binary}")

    with tempfile.TemporaryDirectory(prefix="orhun_package_remove_") as raw:
        root = Path(raw)
        project = root / "project"
        project.mkdir()
        (project / "orhun.yap").write_text(
            'ad: "project"\nsurum: "0.1.0"\nana_dosya: "main.oh"\n',
            encoding="utf-8",
        )

        for name in ("bir", "iki"):
            source = root / f"{name}_source"
            source.mkdir()
            (source / "modul.oh").write_text(f'yaz "{name}"\n', encoding="utf-8")
            installed = run_cmd(
                [str(binary), "paket", "kur", str(source), name],
                project,
            )
            require(
                installed.returncode == 0,
                f"Package install failed ({name}):\n{installed.stdout}\n{installed.stderr}",
            )

        removed = run_cmd([str(binary), "paket", "kaldir", "bir"], project)
        require(
            removed.returncode == 0,
            f"Package removal failed:\n{removed.stdout}\n{removed.stderr}",
        )
        require(not (project / "lib" / "bir").exists(), "Removed package directory remains")
        require((project / "lib" / "iki").is_dir(), "Unrelated package was removed")

        lock_text = (project / "orhun.lock").read_text(encoding="utf-8")
        require("bir|" not in lock_text, "Removed package remains in lock file")
        require("iki|" in lock_text, "Unrelated lock record was removed")
        config_text = (project / "orhun.yap").read_text(encoding="utf-8")
        require("- bir" not in config_text, "Removed package remains in orhun.yap")
        require("- iki" in config_text, "Unrelated dependency was removed from orhun.yap")

        verified = run_cmd([str(binary), "paket", "dogrula"], project)
        require(
            verified.returncode == 0,
            f"Remaining package should verify:\n{verified.stdout}\n{verified.stderr}",
        )

        for unsafe in (".", ".."):
            rejected = run_cmd([str(binary), "paket", "kaldir", unsafe], project)
            require(rejected.returncode != 0, f"Unsafe package name was accepted: {unsafe}")
            require((project / "lib" / "iki").is_dir(), "Unsafe removal changed lib contents")

        missing = run_cmd([str(binary), "paket", "kaldir", "yok"], project)
        require(missing.returncode != 0, "Removing a missing package should fail")

        valid_lock = (project / "orhun.lock").read_text(encoding="utf-8")
        (project / "orhun.lock").write_text(
            valid_lock + "\n..|kaynak|gecersiz|v3|-|gecersiz|\n",
            encoding="utf-8",
        )
        malformed_lock = run_cmd([str(binary), "paket", "kaldir", "iki"], project)
        require(malformed_lock.returncode != 0, "Removal accepted a malformed lock file")
        require(
            (project / "lib" / "iki").is_dir(),
            "Malformed lock must be rejected before deleting the package",
        )
        (project / "orhun.lock").write_text(valid_lock, encoding="utf-8")

        removed_last = run_cmd([str(binary), "paket", "kaldır", "iki"], project)
        require(removed_last.returncode == 0, "Turkish-character removal alias failed")
        require(not (project / "lib" / "iki").exists(), "Last package directory remains")
        require(not (project / "orhun.lock").exists(), "Empty lock file should be removed")

    print("Package removal smoke passed (path containment, lock/config updates, aliases).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
