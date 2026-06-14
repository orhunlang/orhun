#!/usr/bin/env python3
from coverage_gate import parse_coverage_percent


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> int:
    require(parse_coverage_percent("lines: 58.3% (123/211)\n") == 58.3, "legacy gcovr")
    require(parse_coverage_percent("TOTAL 4847 3310 68%\n") == 68.0, "gcovr 7")
    require(parse_coverage_percent("Lines executed:54.32% of 1234\n") == 54.32, "gcov")

    try:
        parse_coverage_percent("coverage unavailable\n")
    except RuntimeError:
        pass
    else:
        raise RuntimeError("invalid coverage summary should fail")

    print("Coverage gate parser smoke passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
