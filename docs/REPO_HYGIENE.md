# Repo Hygiene Plan

This document defines a non-destructive cleanup path for historical local
artifacts.

## Why

- Root currently contains many generated `.exe`, `.o`, `.txt`, and trace files.
- Generated outputs should be grouped under `build/` or `artifacts/local/`.

## Policy

1. Do not auto-delete files.
2. Move local/generated artifacts to `artifacts/local/`.
3. Keep source and test fixtures in place.
4. Keep tracked fixture outputs under `tests/cases/*.expected.txt`.

## Helper Scripts

- PowerShell: `tools/repo_hygiene/move_local_artifacts.ps1`
- Bash: `tools/repo_hygiene/move_local_artifacts.sh`

## Typical Usage

```powershell
pwsh tools/repo_hygiene/move_local_artifacts.ps1
```

```bash
bash tools/repo_hygiene/move_local_artifacts.sh
```

