# Orhun

Orhun is a Turkish-first programming language runtime with:

- a VM execution path
- interpreter fallback controls
- package and lock verification flows
- LSP support over stdio
- CI-driven quality gates

Long-term direction: Orhun starts with a C++ bootstrap core, then moves toward
self-hosting. The goal is for Orhun programs to run without another language
runtime and for more of the compiler/tooling to be written in Orhun itself.

Repository: https://github.com/orhunlanguage/orhun

## Quick Start

Run REPL:

```bash
orhun
```

Run a source file:

```bash
orhun dosya.oh
```

Strict VM mode:

```bash
orhun vm-kati dosya.oh
```

Project health summary:

```bash
orhun doctor
orhun doctor --json
```

## Important Commands

- `orhun hiz <dosya.oh> [--json] [--warmup=N] [--olcum-modu=runtime|full]`
- `orhun lsp --stdio [--workspace-root <path>]`
- `orhun paket kur <kaynak> [paket_adi] [--ref <tag|commit>] [--no-lock]`
- `orhun paket dogrula`
- `orhun paket lock-guncelle`

## Repository Notes

- primary VS Code extension path: `tools/vscode-orhun`
- transition notes: `tools/vscode/README.md`
- migration notes: `docs/MIGRATION_GUIDE.md`
- self-hosting roadmap: `docs/SELF_HOSTING_ROADMAP.md`
- release channels: `docs/RELEASE_CHANNELS.md`
- deprecation policy: `docs/DEPRECATION_POLICY.md`
- security policy: `SECURITY.md`

## Local Artifact Hygiene

Historically generated binaries/logs can be moved under `artifacts/local/`:

- `tools/repo_hygiene/move_local_artifacts.ps1`
- `tools/repo_hygiene/move_local_artifacts.sh`
