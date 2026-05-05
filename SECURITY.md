# Security Policy

## Scope

This project includes:

- VM/interpreter execution paths
- package management and lock verification
- FFI entry points
- command execution helpers
- editor/LSP protocol handling

## Supported Channels

- `stable`: security fixes are prioritized and must remain backward-compatible.
- `beta`: near-stable candidate line.
- `nightly`: fast-moving line, not recommended for production.

## Reporting

Please report vulnerabilities privately first.

- preferred contact: `orhunlang@gmail.com`
- fallback: open a private security advisory in repository settings

Include:

- affected version and commit
- reproduction steps
- impact assessment
- suggested mitigation (if known)

## Security Controls (Current)

- restricted command mode by default (`sistem.komut`)
- FFI policy (`off|allowlist|full`)
- package source allowlist for remote installs
- lock integrity via hash + commit pin checks

## Threat Model Summary

- input-driven parser/compiler crashes
- unsafe shell command injection
- unsafe dynamic library loading
- package source tampering / lock drift
- protocol payload parsing abuse in LSP

## Hardening Direction

- sanitizer + static analysis in CI
- coverage threshold gates
- policy smoke tests for command, FFI, and package allowlist
- stricter benchmark and regression gates
