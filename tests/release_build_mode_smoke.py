#!/usr/bin/env python3
from pathlib import Path


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def require_all(text: str, needles: tuple[str, ...], source: str) -> None:
    for needle in needles:
        require(needle in text, f"{source} is missing release build contract: {needle}")


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    powershell = (repo / "tests" / "run_tests.ps1").read_text(encoding="utf-8")
    shell = (repo / "tests" / "run_tests.sh").read_text(encoding="utf-8")
    workflow = (repo / ".github" / "workflows" / "release.yml").read_text(
        encoding="utf-8"
    )
    readme = (repo / "README.md").read_text(encoding="utf-8")

    require_all(
        powershell,
        ('[ValidateSet("debug", "release")]', '"-O2"', '"-DNDEBUG"'),
        "tests/run_tests.ps1",
    )
    require_all(
        shell,
        (
            'BUILD_MODE="${3:-debug}"',
            "compiler_args=(-std=c++17 -Wall -Wextra -pedantic)",
            "release) compiler_args+=(-O2 -DNDEBUG)",
            '"${COMPILER}" "${compiler_args[@]}"',
        ),
        "tests/run_tests.sh",
    )
    require(
        "OPT_FLAGS=()" not in shell,
        "tests/run_tests.sh must not expand an empty array under macOS Bash 3.2",
    )
    require_all(
        workflow,
        (
            "run_tests.ps1 -Output build/orhun_release.exe -BuildMode release",
            "run_tests.sh g++ build/orhun_release release",
            "run_tests.sh clang++ build/orhun_release release",
        ),
        ".github/workflows/release.yml",
    )
    require_all(
        readme,
        (
            "-O2 -DNDEBUG",
            "run_tests.ps1 -Output build/orhun_release.exe -BuildMode release",
            "run_tests.sh g++ build/orhun_release release",
        ),
        "README.md",
    )

    print("Release build mode smoke passed (PowerShell, POSIX, workflow, docs).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
