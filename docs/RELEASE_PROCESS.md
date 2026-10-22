# Orhun 1.0.0 Release Process

This checklist is the operational path from a green `main` to a `v1.0.0` tag.

## Preconditions (code)

- [ ] `python tests/release_readiness_smoke.py ./build/orhun_test.exe` passes
- [ ] `tests/run_tests.ps1` full suite green
- [ ] `tests/vm_parity.ps1` reports `vm_parity_fail=0`
- [ ] `python tests/roadmap_smoke.py ./build/orhun_test.exe` passes
- [ ] `docs/KNOWN_ISSUES.md` reviewed for anything that must be fixed first
- [ ] `docs/MIGRATION_GUIDE.md` covers every break since `0.9.0`
- [ ] `docs/SPEC.md` matches implementation (keyword contract smoke)

## Preconditions (versioning)

- [ ] `VERSION` is `1.0.0`
- [ ] `Interpreter.h` `ORHUN_SURUM` is `1.0.0`
- [ ] README `Current version: \`1.0.0\``
- [ ] `python tests/version_consistency_smoke.py ./build/orhun_test.exe` passes

## Release commit

1. Bump version strings in one commit: `build: bump version to 1.0.0`
2. Tag annotated: `git tag -a v1.0.0 -m "Orhun 1.0.0"`
3. Push branch and tag (maintainer action)
4. Let `.github/workflows/release.yml` publish archives + SHA-256
5. Attach `docs/RELEASE_NOTES_1.0.0.md` (or changelog section) to the GitHub release

## Post-release

- [ ] Verify `orhun surum` on published binaries prints `Orhun v1.0.0`
- [ ] Verify `orhun doctor --json` reports `status: ready` on a clean install
- [ ] File follow-ups for remaining `docs/KNOWN_ISSUES.md` items under `2.1.0`

## Source-only fallback

If binary signing is not ready, the release **must** state that it is
source-only and list verified build commands from `README.md` /
`CONTRIBUTING.md`. Do not silently skip the binary bar without documenting it.
