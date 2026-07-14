#!/usr/bin/env python3
import json
import re
from pathlib import Path


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    package_path = repo / "tools" / "vscode-orhun" / "package.json"
    syntax_path = repo / "tools" / "vscode-orhun" / "syntaxes" / "orhun.tmLanguage.json"
    snippets_path = repo / "tools" / "vscode-orhun" / "snippets" / "orhun.code-snippets"

    package = json.loads(package_path.read_text(encoding="utf-8"))
    snippets = json.loads(snippets_path.read_text(encoding="utf-8"))
    grammar = json.loads(syntax_path.read_text(encoding="utf-8"))

    snippet_contribs = package.get("contributes", {}).get("snippets", [])
    require(snippet_contribs, "VS Code package should contribute snippets")
    require(
        any(
            item.get("language") == "orhun"
            and item.get("path") == "./snippets/orhun.code-snippets"
            for item in snippet_contribs
        ),
        "VS Code package snippet contribution is missing or stale",
    )

    includes = [item.get("include") for item in grammar.get("patterns", [])]
    require("#builtins" in includes, "VS Code grammar should include #builtins")

    builtins = grammar.get("repository", {}).get("builtins", {}).get("patterns", [])
    require(builtins, "VS Code grammar missing builtins patterns")

    keyword_patterns = grammar.get("repository", {}).get("keywords", {}).get("patterns", [])
    keyword_combined = "\n".join(str(pattern.get("match", "")) for pattern in keyword_patterns)
    require(re.search(r"(?<![A-Za-z_])her(?![A-Za-z_])", keyword_combined),
            "VS Code keyword pattern missing her")

    combined = "\n".join(str(pattern.get("match", "")) for pattern in builtins)
    for word in (
        "yaz",
        "oku",
        "aralik",
        "aralık",
        "ilk",
        "son",
        "bos_mu",
        "boş_mu",
        "dolu_mu",
        "json",
        "dosya",
        "token_araligi",
        "ifade_satir_araligi",
        "komut_satir_araligi",
        "tum_komut_satir_araliklari",
        "hata_tanilari",
        "tani_listesi_bicimlendir",
        "tani_listesi_ozeti",
        "tani_listesi_seviyeye_gore_filtrele",
        "dugum_turu_var_mi",
        "dugum_derinligi",
        "dugum_ozeti",
    ):
        require(re.search(rf"(?<![A-Za-z_]){re.escape(word)}(?![A-Za-z_])", combined),
                f"VS Code builtins pattern missing {word}")

    required_snippets = {
        "Yaz": "yaz",
        "Oku": "oku",
        "Eğer": "eger",
        "İşlev": "islev",
        "Aralık Döngüsü": "aralik",
        "Her Döngüsü": "her",
        "Numaralandır": "numaralandir",
        "Eşleştir": "eslestir",
        "Dil Yardımcısı": "dil",
        "Lexer Özeti": "lexer",
        "Parser Özeti": "parser",
        "Tanı Listesi": "tani",
        "AST Gezgini": "ast",
    }
    for name, prefix in required_snippets.items():
        require(name in snippets, f"VS Code snippet missing {name}")
        snippet = snippets[name]
        require(snippet.get("prefix") == prefix, f"VS Code snippet prefix stale: {name}")
        body = "\n".join(snippet.get("body", []))
        require(body.strip(), f"VS Code snippet body empty: {name}")

    require("oku(" in "\n".join(snippets["Oku"]["body"]), "Oku snippet should call oku")
    require("aralik(" in "\n".join(snippets["Aralık Döngüsü"]["body"]),
            "Aralik snippet should call aralik")
    require("her " in "\n".join(snippets["Her Döngüsü"]["body"]),
            "Her snippet should use her loop syntax")
    require("koleksiyon.numaralandir(" in "\n".join(snippets["Numaralandır"]["body"]),
            "Numaralandir snippet should call koleksiyon.numaralandir")
    require("koleksiyon.eslestir(" in "\n".join(snippets["Eşleştir"]["body"]),
            "Eslestir snippet should call koleksiyon.eslestir")
    require("dil.token_degerleri(" in "\n".join(snippets["Dil Yardımcısı"]["body"]),
            "Dil snippet should expose token summaries")
    require("dil.tani_listesi_bicimlendir(" in "\n".join(snippets["Dil Yardımcısı"]["body"]),
            "Dil snippet should expose diagnostic-list formatting")
    require("dil.tani_listesi_ozeti(" in "\n".join(snippets["Dil Yardımcısı"]["body"]),
            "Dil snippet should expose diagnostic-list summaries")
    require("lexer.hata_degerleri(" in "\n".join(snippets["Lexer Özeti"]["body"]),
            "Lexer snippet should expose error summaries")
    require("lexer.token_araligi(" in "\n".join(snippets["Lexer Özeti"]["body"]),
            "Lexer snippet should expose token ranges")
    require("parser.hata_var_mi(" in "\n".join(snippets["Parser Özeti"]["body"]),
            "Parser snippet should expose parser error helpers")
    require("parser.komut_satir_araligi(" in "\n".join(snippets["Parser Özeti"]["body"]),
            "Parser snippet should expose command ranges")
    require("parser.ifade_satir_araligi(" in "\n".join(snippets["Parser Özeti"]["body"]),
            "Parser snippet should expose expression ranges")
    require("parser.tum_komut_satir_araliklari(" in "\n".join(snippets["Parser Özeti"]["body"]),
            "Parser snippet should expose recursive command ranges")
    require("parser.hata_tanilari(" in "\n".join(snippets["Parser Özeti"]["body"]),
            "Parser snippet should expose parser diagnostics")
    require("dil.tani_listesi_bicimlendir(" in "\n".join(snippets["Tanı Listesi"]["body"]),
            "Tani snippet should format diagnostic lists")
    require("dil.tani_listesi_ozeti(" in "\n".join(snippets["Tanı Listesi"]["body"]),
            "Tani snippet should summarize diagnostic lists")
    require("dil.tani_listesi_seviyeye_gore_filtrele(" in "\n".join(snippets["Tanı Listesi"]["body"]),
            "Tani snippet should filter diagnostic lists")
    require("dil.dugum_turlerini_duzlestir(" in "\n".join(snippets["AST Gezgini"]["body"]),
            "AST snippet should flatten node types")
    require("dil.dugum_turu_var_mi(" in "\n".join(snippets["AST Gezgini"]["body"]),
            "AST snippet should query node types")
    require("dil.dugum_ozeti(" in "\n".join(snippets["AST Gezgini"]["body"]),
            "AST snippet should summarize node trees")

    print("VS Code tooling smoke passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
