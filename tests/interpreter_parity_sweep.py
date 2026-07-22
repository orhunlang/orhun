#!/usr/bin/env python3
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


WINDOWS_ONLY = {
    "ffi_dis_islev",
    "ffi_kernel32",
    "ffi_symbol",
    "ffi_tanimli_kernel32",
    "ffi_text",
}

KNOWN_GAPS = {
    "stdlib_orhun_derleyici",
    "stdlib_orhun_paket",
    "stdlib_orhun_parser",
}

TIMEOUT_FLOORS = {
    "gc_stress": 30.0,
    "stdlib_orhun_lexer": 20.0,
}


def normalize(value: str) -> str:
    return value.replace("\r\n", "\n").rstrip("\n")


def decode_timeout_output(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def first_difference(expected: str, actual: str) -> str:
    expected_lines = expected.splitlines()
    actual_lines = actual.splitlines()
    for index in range(max(len(expected_lines), len(actual_lines))):
        wanted = expected_lines[index] if index < len(expected_lines) else "<end>"
        got = actual_lines[index] if index < len(actual_lines) else "<end>"
        if wanted != got:
            return f"line {index + 1}: expected={wanted!r} actual={got!r}"
    return "output differs"


def resolve_binary(raw: str, repo: Path) -> Path:
    candidate = Path(raw)
    if not candidate.is_absolute():
        candidate = (Path.cwd() / candidate).resolve()
    if not candidate.exists():
        candidate = (repo / raw).resolve()
    return candidate


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare the C++ interpreter with guarded runtime outputs"
    )
    parser.add_argument("binary", help="Orhun executable")
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument(
        "--discover",
        action="store_true",
        help="report all mismatches without enforcing the known-gap set",
    )
    args = parser.parse_args()

    repo = Path(__file__).resolve().parents[1]
    binary = resolve_binary(args.binary, repo)
    if not binary.exists():
        raise RuntimeError(f"Binary not found: {binary}")

    cases_dir = repo / "tests" / "cases"
    work_root = repo / "build" / "test-work" / "interpreter-parity"
    work_root.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env["ORHUN_STDLIB_PATH"] = os.pathsep.join(
        (str(repo / "StdLib"), str(repo))
    )

    exact: list[str] = []
    mismatches: dict[str, str] = {}
    # Orhun stdout/stderr is UTF-8 on every supported platform. Using the
    # active Windows code page here silently corrupts Turkish diagnostics.
    runtime_encoding = "utf-8"
    expected_paths = sorted(cases_dir.glob("*.expected.txt"))
    for expected_path in expected_paths:
        name = expected_path.name.removesuffix(".expected.txt")
        source = cases_dir / f"{name}.oh"
        if not source.exists():
            continue
        if os.name != "nt" and name in WINDOWS_ONLY:
            continue

        work_dir = work_root / name
        if work_dir.exists():
            shutil.rmtree(work_dir)
        work_dir.mkdir(parents=True)

        case_env = env.copy()
        if name == "turkce_kati_alias":
            case_env["ORHUN_TURKCE_KATI"] = "1"

        try:
            case_timeout = max(args.timeout, TIMEOUT_FLOORS.get(name, 0.0))
            proc = subprocess.run(
                [str(binary), "yorumla", str(source.resolve())],
                cwd=work_dir,
                env=case_env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding=runtime_encoding,
                errors="replace",
                timeout=case_timeout,
            )
            actual = normalize(proc.stdout + proc.stderr)
        except subprocess.TimeoutExpired as ex:
            actual = normalize(
                decode_timeout_output(ex.stdout) + decode_timeout_output(ex.stderr)
            )
            mismatches[name] = f"timeout after {case_timeout:g}s; {actual!r}"
            continue

        expected = normalize(expected_path.read_text(encoding="utf-8"))
        if actual == expected and proc.returncode in (0, 1):
            exact.append(name)
            continue

        detail = first_difference(expected, actual)
        if proc.returncode not in (0, 1):
            detail += f"; exit={proc.returncode}"
        mismatches[name] = detail

    print(
        f"Interpreter parity sweep: {len(exact)} exact, "
        f"{len(mismatches)} mismatches."
    )
    for name, detail in sorted(mismatches.items()):
        print(f"[GAP] {name}: {detail}")

    if args.discover:
        return 0

    # New mismatches fail; resolved gaps are allowed and reported.
    unexpected = sorted(set(mismatches) - KNOWN_GAPS)
    if unexpected:
        print("Unexpected interpreter parity gaps: " + ", ".join(unexpected))
        return 1

    resolved = sorted(KNOWN_GAPS - set(mismatches))
    if resolved:
        print("Resolved interpreter parity gaps: " + ", ".join(resolved))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
