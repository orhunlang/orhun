#!/usr/bin/env python3
import argparse
import os
import shutil
import subprocess
import tempfile
from pathlib import Path


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def run(
    args: list[str], cwd: Path, env: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=cwd,
        env=env,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify a runtime binary discovers its sibling source StdLib"
    )
    parser.add_argument("binary", help="Orhun executable path")
    args = parser.parse_args()

    repo = Path(__file__).resolve().parents[1]
    binary = Path(args.binary).resolve()
    require(binary.is_file(), f"Binary not found: {binary}")

    with tempfile.TemporaryDirectory(prefix="orhun_runtime_bundle_") as raw:
        temp = Path(raw)
        bundle = temp / "bundle"
        work = temp / "work"
        bundle.mkdir()
        work.mkdir()

        installed_binary = bundle / ("orhun.exe" if os.name == "nt" else "orhun")
        shutil.copy2(binary, installed_binary)
        shutil.copytree(repo / "StdLib", bundle / "StdLib")
        if os.name != "nt":
            installed_binary.chmod(0o755)

        source = work / "program.oh"
        source.write_text(
            "\n".join(
                [
                    'koleksiyon olsun dahil_et "orhun/koleksiyon.oh"',
                    "yazdır koleksiyon.numaralandir([7, 8], 3)",
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )

        expected = "[[3, 7], [4, 8]]"
        for mode in ([], ["vm-kati"]):
            proc = run([str(installed_binary), *mode, str(source)], work)
            require(
                proc.returncode == 0,
                f"Sibling StdLib run failed ({mode or ['default']}):\n"
                f"{proc.stdout}\n{proc.stderr}",
            )
            require(proc.stdout.strip() == expected, "Sibling StdLib output changed")

        path_env = os.environ.copy()
        path_key = next(
            (key for key in path_env if key.casefold() == "path"),
            "PATH",
        )
        path_env[path_key] = str(bundle) + os.pathsep + path_env.get(path_key, "")
        if os.name == "nt":
            proc = run(
                [
                    os.environ.get("COMSPEC", "cmd.exe"),
                    "/d",
                    "/c",
                    "orhun",
                    str(source),
                ],
                work,
                path_env,
            )
        else:
            proc = run(
                ["/bin/sh", "-c", 'orhun "$1"', "orhun", str(source)],
                work,
                path_env,
            )
        require(
            proc.returncode == 0 and proc.stdout.strip() == expected,
            "PATH-invoked runtime did not discover its sibling StdLib:\n"
            f"{proc.stdout}\n{proc.stderr}",
        )

        custom = temp / "custom-stdlib"
        custom.mkdir()
        env = os.environ.copy()
        env["ORHUN_STDLIB_PATH"] = str(custom)
        proc = run([str(installed_binary), str(source)], work, env)
        require(
            proc.returncode == 0 and proc.stdout.strip() == expected,
            "Sibling StdLib must remain a fallback after ORHUN_STDLIB_PATH",
        )

    print("Runtime bundle smoke passed (sibling source StdLib discovery).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
