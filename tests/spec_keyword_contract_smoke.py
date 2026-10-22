#!/usr/bin/env python3
"""SPEC keyword contract: parser/lexer keyword lists stay documented."""

from __future__ import annotations

import re
from pathlib import Path


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def quoted(block: str) -> set[str]:
    return set(re.findall(r'"([^"]+)"', block))


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    spec = (repo / "docs" / "SPEC.md").read_text(encoding="utf-8")
    parser = (repo / "Parser.cpp").read_text(encoding="utf-8")
    lexer = (repo / "Lexer.cpp").read_text(encoding="utf-8")

    core_match = re.search(
        r"Current Turkish keywords:\s*```text\s*(.*?)```", spec, re.S
    )
    builtin_match = re.search(
        r"Beginner / builtin command names.*?```text\s*(.*?)```", spec, re.S
    )
    alias_match = re.search(
        r"Compatibility alias:\s*```text\s*(.*?)```", spec, re.S
    )
    eng_match = re.search(
        r"English keyword aliases.*?```text\s*(.*?)```", spec, re.S
    )
    require(core_match is not None, "SPEC missing core keyword block")
    require(builtin_match is not None, "SPEC missing builtin command block")
    require(alias_match is not None, "SPEC missing compatibility alias block")
    require(eng_match is not None, "SPEC missing English alias block")

    spec_core = set(core_match.group(1).split())
    spec_builtins = set(builtin_match.group(1).split())
    spec_aliases = set(alias_match.group(1).split())
    spec_english = set(eng_match.group(1).split())

    parser_match = re.search(
        r"orhunAnahtarKelimeleri\(\) \{.*?anahtarlar = \{(.*?)\};",
        parser,
        re.S,
    )
    require(parser_match is not None, "Parser.cpp missing keyword table")
    parser_words = quoted(parser_match.group(1))

    lexer_match = re.search(r"anahtarKelimeler = \{(.*?)\};", lexer, re.S)
    require(lexer_match is not None, "Lexer.cpp missing keyword table")
    lexer_words = set(re.findall(r'U"([^"]+)"', lexer_match.group(1)))

    require(
        spec_core <= parser_words,
        f"SPEC core keywords missing from parser: {sorted(spec_core - parser_words)}",
    )
    require(
        spec_builtins <= parser_words,
        f"SPEC builtin names missing from parser: {sorted(spec_builtins - parser_words)}",
    )
    require(
        spec_aliases <= parser_words,
        f"SPEC aliases missing from parser: {sorted(spec_aliases - parser_words)}",
    )
    require(
        lexer_words <= parser_words,
        f"Lexer keywords missing from parser: {sorted(lexer_words - parser_words)}",
    )
    require(
        spec_english,
        "SPEC English alias block is empty",
    )

    undocumented = parser_words - spec_core - spec_builtins - spec_aliases
    # 'yaz' and friends are documented as builtins; anything else must be listed.
    require(
        not undocumented,
        f"Parser keywords not documented in SPEC: {sorted(undocumented)}",
    )

    print(
        "Spec keyword contract smoke passed "
        f"(core={len(spec_core)}, builtins={len(spec_builtins)}, "
        f"aliases={len(spec_aliases)}, english={len(spec_english)})."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
