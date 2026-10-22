# Orhun 1.0.1 Release Notes

Patch release after the 1.0.0 stable language contract.

## Highlights

### Official one-line installers

```bash
curl -fsSL https://raw.githubusercontent.com/orhunlang/orhun/v1.0.1/install.sh | bash
```

```powershell
irm https://raw.githubusercontent.com/orhunlang/orhun/v1.0.1/install.ps1 | iex
```

Both scripts download the matching `orhun-runtime-1.0.1-<platform>` archive
from GitHub Releases, verify `SHA256SUMS`, and put `orhun` on `PATH`.
`install.sh` / `install.ps1` are also published as release assets.

### setup-orhun GitHub Action

`orhunlang/orhun/setup-orhun@v1.0.1` installs a verified toolchain in CI and
is Marketplace-ready (`action.yml` branding, docs, composite steps).

### VS Code extension 1.0.1 package line

`tools/vscode-orhun` ships grammar coverage for English keyword aliases and
ASCII comparison operators (`==`, `!=`, `<`, `>`, `<=`, `>=`, `!`).
Package with `npm run package` → `orhun-language-1.0.1.vsix`.

## Compatibility

No language or runtime behavior changes from 1.0.0. Safe patch upgrade.

## Verification

- Full case suite green
- VM parity 153/0
- `tests/install_packaging_smoke.py` green
- `tests/release_readiness_smoke.py` green
