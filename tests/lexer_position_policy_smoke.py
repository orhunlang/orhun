#!/usr/bin/env python3
from pathlib import Path


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def has_non_ascii(text: str) -> bool:
    return any(ord(char) > 127 for char in text)


def first_line(text: str) -> str:
    lines = text.splitlines()
    return lines[0] if lines else ""


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    fixture_dir = repo / "tests" / "lexer_parity"
    fixtures = sorted(fixture_dir.glob("*.oh"))
    require(fixtures, f"No lexer parity fixtures found under {fixture_dir}")

    non_ascii = []
    for fixture in fixtures:
        text = fixture.read_text(encoding="utf-8")
        if has_non_ascii(text):
            header = first_line(text)
            require(
                "parity: tokens-only" not in header,
                f"{fixture} contains non-ASCII text and must compare UTF-8 "
                "line/column positions",
            )
            non_ascii.append(fixture.name)

    require(non_ascii, "Expected at least one non-ASCII lexer parity fixture")
    print(
        "Lexer position policy smoke passed "
        f"({len(non_ascii)} non-ASCII fixtures with position parity)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
