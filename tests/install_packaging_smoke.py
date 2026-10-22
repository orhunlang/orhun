#!/usr/bin/env python3
"""Installer / VS Code / setup-orhun packaging contract smoke."""

from __future__ import annotations

import json
from pathlib import Path

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover - optional
    yaml = None


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> int:
    repo = Path.cwd()
    version = (repo / "VERSION").read_text(encoding="utf-8").strip()

    sh = (repo / "install.sh").read_text(encoding="utf-8")
    ps1 = (repo / "install.ps1").read_text(encoding="utf-8")
    require("releases/download/v" in sh, "install.sh must use GitHub Releases")
    require("SHA256SUMS" in sh, "install.sh must verify checksums")
    require("releases/download/v" in ps1, "install.ps1 must use GitHub Releases")
    require("SHA256SUMS" in ps1, "install.ps1 must verify checksums")
    require("ORHUN_VERSION" in sh and "ORHUN_VERSION" in ps1, "installer version env")
    print("[OK] installers")

    ext_root = repo / "tools" / "vscode-orhun"
    pkg = json.loads((ext_root / "package.json").read_text(encoding="utf-8"))
    require(pkg.get("version") == version, "vscode package.json version mismatch")
    grammar = json.loads(
        (ext_root / "syntaxes" / "orhun.tmLanguage.json").read_text(encoding="utf-8")
    )
    text = json.dumps(grammar, ensure_ascii=False)
    for needle in ("==", "!=", "<=", ">=", "keyword.operator.comparison.orhun"):
        require(needle in text, f"grammar missing {needle!r}")
    for kw in ("eğer", "işlev", "if", "function", "print"):
        require(kw in text, f"grammar missing keyword {kw!r}")
    vsix = list(ext_root.glob("*.vsix"))
    require(vsix, "vsix package missing (run npm run package)")
    print(f"[OK] vscode ({vsix[0].name})")

    action = repo / "setup-orhun" / "action.yml"
    require(action.exists(), "setup-orhun/action.yml missing")
    raw = action.read_text(encoding="utf-8")
    require("name:" in raw and "description:" in raw, "action.yml needs name/description")
    require("branding:" in raw, "action.yml needs branding for Marketplace")
    require("inputs:" in raw and "outputs:" in raw, "action.yml needs inputs/outputs")
    require("composite" in raw, "action.yml must be composite")
    require((repo / "setup-orhun" / "scripts" / "install.sh").exists(), "action installer missing")
    require((repo / "setup-orhun" / "README.md").exists(), "action README missing")
    if yaml is not None:
        parsed = yaml.safe_load(raw)
        require(isinstance(parsed, dict), "action.yml must be a mapping")
        require(parsed.get("name"), "action.yml name empty")
        branding = parsed.get("branding") or {}
        require(branding.get("icon"), "branding.icon required for Marketplace")
        require(branding.get("color"), "branding.color required for Marketplace")
    print("[OK] setup-orhun")

    readme = (repo / "README.md").read_text(encoding="utf-8")
    require("install.sh" in readme and "install.ps1" in readme, "README missing installers")
    require("setup-orhun" in readme, "README missing setup-orhun")
    print("[OK] readme-install")

    print("Installer/packaging contract smoke passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
