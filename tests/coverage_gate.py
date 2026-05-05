#!/usr/bin/env python3
import argparse
import re
from pathlib import Path


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def parse_coverage_percent(summary_text: str) -> float:
    # Expected gcovr line sample: "lines: 58.3% (123/211)"
    m = re.search(r"^lines:\s*([0-9]+(?:\.[0-9]+)?)%", summary_text, re.MULTILINE)
    if m:
        return float(m.group(1))

    # Fallback gcov line sample: "Lines executed:54.32% of 1234"
    m = re.search(r"Lines executed:([0-9]+(?:\.[0-9]+)?)%", summary_text)
    if m:
        return float(m.group(1))

    raise RuntimeError("coverage percent could not be parsed from summary")


def main() -> int:
    parser = argparse.ArgumentParser(description="Orhun coverage threshold gate")
    parser.add_argument("--summary", default="coverage/summary.txt", help="Coverage summary file")
    parser.add_argument("--min-lines", type=float, default=55.0, help="Minimum line coverage percent")
    args = parser.parse_args()

    summary = Path(args.summary)
    if not summary.exists():
        print(f"Coverage summary not found: {summary}")
        return 3

    text = summary.read_text(encoding="utf-8", errors="replace")
    try:
        lines_percent = parse_coverage_percent(text)
    except RuntimeError as ex:
        print(f"[FAIL] {ex}")
        return 3

    print(f"[COVERAGE] lines={lines_percent:.2f}% min={args.min_lines:.2f}%")
    if lines_percent < args.min_lines:
        print("[FAIL] Coverage threshold failed.")
        return 2

    print("Coverage gate passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

