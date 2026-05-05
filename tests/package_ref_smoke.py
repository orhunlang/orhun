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


def git(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return run_cmd(["git", *args], cwd)


def main() -> int:
    parser = argparse.ArgumentParser(description="Package --ref smoke test")
    parser.add_argument("binary", help="Orhun executable")
    args = parser.parse_args()

    binary = Path(args.binary).resolve()
    if not binary.exists():
        raise SystemExit(f"Binary not found: {binary}")

    with tempfile.TemporaryDirectory(prefix="orhun_pkg_ref_") as tmp:
        root = Path(tmp)
        src = root / "kaynak_repo"
        src.mkdir(parents=True, exist_ok=True)

        require(git(src, "init").returncode == 0, "git init failed")
        require(git(src, "config", "user.email", "orhun@example.com").returncode == 0, "git config email failed")
        require(git(src, "config", "user.name", "Orhun Bot").returncode == 0, "git config name failed")

        mod = src / "modul.oh"
        mod.write_text("yazdir 1\n", encoding="utf-8")
        require(git(src, "add", ".").returncode == 0, "git add failed")
        require(git(src, "commit", "-m", "v1").returncode == 0, "git commit v1 failed")
        first = git(src, "rev-parse", "HEAD")
        require(first.returncode == 0, "git rev-parse v1 failed")
        first_commit = first.stdout.strip()

        mod.write_text("yazdir 2\n", encoding="utf-8")
        require(git(src, "add", ".").returncode == 0, "git add v2 failed")
        require(git(src, "commit", "-m", "v2").returncode == 0, "git commit v2 failed")

        work = root / "workspace"
        work.mkdir(parents=True, exist_ok=True)

        kur = run_cmd(
            [str(binary), "paket", "kur", str(src), "deneme_paket", "--ref", first_commit],
            work,
        )
        require(kur.returncode == 0, f"paket kur --ref failed: {kur.stdout}\n{kur.stderr}")

        lock = work / "orhun.lock"
        require(lock.exists(), "orhun.lock missing after --ref install")
        text = lock.read_text(encoding="utf-8")
        require(first_commit.lower() in text.lower(), "lock file missing pinned commit")
        require(first_commit in text, "lock file missing source_ref value")

        dogrula = run_cmd([str(binary), "paket", "dogrula"], work)
        require(dogrula.returncode == 0, f"paket dogrula failed: {dogrula.stdout}\n{dogrula.stderr}")

    print("Package --ref smoke passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

