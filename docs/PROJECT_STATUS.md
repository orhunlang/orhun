# Orhun Project Status

This document gives a human-readable snapshot of where Orhun is today and what
still has to become true before it can be treated as a stable, production-ready
language.

## Current Version

- Public version: `0.8.0`
- Stability: experimental / pre-1.0
- README current-version line: `0.8.0`
- Version source of truth: `VERSION`

Normal development commits do not change the public version number. Version
bumps should happen in release commits after the relevant gates are met.

## Progress Estimate

These percentages are planning estimates, not promises.

| Target | Estimated Progress | Meaning |
| --- | ---: | --- |
| Working experimental language / MVP | 55-60% | Orhun already has a lexer, parser, interpreter, bytecode compiler, VM, stdlib surface, package/security flows, tests, and tooling. |
| 1.0 stable language | 35-40% | Needs a stable spec, compatibility policy, release binaries, cleaner docs, stronger package flow, and hardened performance/security gates. |
| 2.1.0 production-ready product bar | 20-25% | Needs 1.0 stability plus ecosystem confidence: installers, docs, examples, package policy, support process, performance gates, and broad CI/nightly coverage. |
| Full self-hosting / independent compiler path | ~60% | The Orhun-written compiler has exact bytecode parity across every current runtime case accepted by C++, ships as a source-free portable compiler bundle that directly emits byte-identical artifacts, passes a three-stage byte-identical self-rebuild gate, and has a tag-triggered multi-platform release path. The serialization bridge and runtime are still C++. |

## What Is Already Real

- Turkish-first syntax and diagnostics.
- UTF-8 identifiers and Turkish keywords.
- Interpreter and strict VM execution paths.
- Bytecode compiler.
- Functions, lambdas, default arguments, classes, inheritance, collections,
  slicing, safe access, and error handling.
- File, JSON, regex, date/time, database helper, server, task, FFI, and system
  policy surfaces.
- Formatter, linter, LSP, VS Code tooling, package/lock verification, and CI.
- Orhun-written lexer/parser prototypes and a bytecode compiler subset covering
  expressions, collections, control flow, functions, closures, lambdas,
  list comprehensions, parallel task plans, external declarations, class
  fields/methods/inheritance, locals, and optimizations with parity smoke tests.
- Exact Orhun/C++ compiler bytecode parity across all current C++-compileable
  runtime cases, guarded by a full-case sweep.
- Strict decoded-bytecode execution bridge from the Orhun-written compiler to
  the C++ VM, guarded by end-to-end bootstrap tests.
- Experimental single-command `orhun-vm` path through the Orhun-written
  compiler and validated C++ VM bridge.
- Experimental `orhun-derle` artifact path with byte-identical `.obc` output
  against the C++ compiler for guarded bootstrap fixtures.
- Bootstrap self-source compile: `StdLib/orhun/derleyici.oh` compiles through
  `orhun-derle` into the same `.obc` bytes as the C++ compiler.
- Explicit `obc-only` module mode runs the precompiled Orhun
  compiler/parser/lexer chain without requiring `.oh` sources or silently
  falling back to C++ source compilation.
- `bootstrap-hazirla` produces the source-free compiler/parser/lexer plus
  compiler-CLI artifact toolchain and a size/CRC32/SHA-256-bearing
  machine-readable manifest in one command.
- `bootstrap-dogrula` validates the complete prepared-toolchain contract,
  payload integrity, and OBC structure before distribution or execution.
- `bootstrap-derle` consumes a prepared toolchain in strict `obc-only` mode
  without requiring environment-variable setup.
- `bootstrap-calistir` uses the same prepared toolchain contract for a
  source-free compiler-module run path.
- `bootstrap-derleyici-paketle` creates a portable source-free
  `orhun-derleyici` executable bundle that discovers and validates its sibling
  strict toolchain before emitting bytecode JSON or complete `.obc`, packaged
  executable, and metadata artifacts.
- The portable compiler's source/output argument parsing and complete artifact
  plan are owned by Orhun-written `derleyici_cli.oh`, including all output
  paths and the metadata source name. The plan is versioned as
  `orhun-artifact-plan-v1`; C++ remains only as the strict plan-validation and
  OBC/package serialization bootstrap bridge. Artifact publication stages the
  complete output set first and preserves existing outputs when staging fails.
- The packaged compiler C++ host no longer recognizes individual compiler CLI
  command names; Orhun-written CLI bytecode returns the structured exit code
  and optional complete artifact plan for every invocation.
- Portable compiler startup strictly validates its compiler-bundle manifest,
  embedded CLI payload size/CRC32/SHA-256, and sibling toolchain link. Source-
  free toolchain module manifests carry the same v2 integrity fields, while v1
  manifests remain verifiable. Bundle identity is manifest/payload based, so
  the executable can be safely renamed.
- `bootstrap-derleyici-dogrula` performs the same complete compiler-bundle
  verification before CI upload or release packaging.
- `bootstrap-yeniden-uret` performs a seed -> stage 2 -> stage 3 rebuild and
  rejects the result unless every generated compiler artifact is byte-identical
  across the final two stages.
- Rebuild results carry an `orhun-bootstrap-rebuild-v2` evidence manifest with
  per-module size, CRC32, and SHA-256 identity; `bootstrap-yeniden-dogrula`
  verifies that evidence and the companion strict toolchain later.
- The compiler bootstrap and self-rebuild gate runs on Windows, Ubuntu, and
  macOS in both the main CI and nightly matrices.
- Main CI builds and uploads validated source-free portable compiler bundles
  for Windows, Linux, and macOS after the self-rebuild gate passes.
- Matching version tags run the full gate on all three platforms and publish
  deterministic versioned compiler and runtime archives, per-archive SHA-256
  files, and a combined `SHA256SUMS` manifest as GitHub Release assets.
- Runtime archives carry the platform `orhun` executable and source standard
  library; the executable discovers its sibling `StdLib` outside the repository.
- `orhun doctor` distinguishes healthy source checkouts from installed portable
  runtime bundles and reports the resolved executable/sibling-StdLib layout.
- Releases publish a cross-platform compiler/runtime installer that requires
  SHA-256 verification and rejects unsafe archive entries before installation.
- Compiled OBC artifacts carry `orhun-obc-v2` metadata with size, CRC32, and
  SHA-256; `obc-dogrula`/`obc-verify` validates the artifact without executing
  it while retaining `orhun-obc-v1` compatibility.
- Packaged executables carry an `ORHNPKG2` size/CRC32/SHA-256 trailer;
  `paketli-dogrula`/`packaged-verify` validates embedded OBC without execution
  while retaining `ORHNPKG1` compatibility.
- Release assets receive signed GitHub/Sigstore build-provenance attestations
  without storing a long-lived signing key in the repository.
- Beginner-friendly `yaz` print alias, `oku` input alias, global
  `aralik`/`aralık` range helper, and simple collection helpers without
  reserving those words as keywords.
- Beginner-friendly `her ... içinde ...` list loops with interpreter, VM,
  parser, Orhun-parser, and Orhun-compiler parity, including `kır` / `devam`
  loop control.
- Multiline list and dictionary literals with optional trailing commas,
  including matching Orhun-written parser/compiler parity.
- Multiline function, method, and constructor calls with optional trailing
  commas, plus multiline parenthesized expressions.
- Multiline named, method, anonymous, and external-function parameter lists
  with optional trailing commas and multiline default values.
- Multiline index and slice access with matching interpreter, VM, and
  Orhun-written parser/compiler behavior.
- Operator-led expression continuation inside open delimiters without changing
  normal newline and block semantics.
- Multiline postfix chains inside open delimiters, including calls, fields,
  safe fields, indexes, and slices.
- Blank lines and comments are layout inside multiline delimiter expressions,
  guarded across the interpreter, VM, and Orhun-written parser/compiler paths.
- Consistent `sistem.argumanlar` program arguments across direct VM,
  interpreter, OBC, packaged executable, and bootstrap execution paths.
- Windows command-line arguments are decoded from the native wide-character
  command line into UTF-8, preserving Turkish paths, aliases, and program args.
- Interpreter/VM parity covers modulo arithmetic and in-place
  `listeye_ekle` list mutation.
- The Orhun-written package manifest helper validates package/dependency names
  and Semantic Versioning 2.0 versions, including prerelease/build identifiers,
  compares valid versions with Semantic Versioning precedence, and evaluates
  exact, comparison, caret, and tilde version rules for future dependency
  resolution. It also parses and structurally validates compatible v1/v2/v3
  lock records in Orhun before a future resolver accesses package paths, and
  produces dependency-first plans while rejecting missing, duplicate, and
  cyclic manifest graphs. It can also select the highest SemVer-compatible
  candidate for each versioned dependency request, including optional manifest
  `bagimlilik_istekleri` validation.
- Package removal is path-contained to a direct `lib/<package>` directory and
  updates both `orhun.lock` and `orhun.yap`; `.` and `..` package names are
  rejected by both the CLI and Orhun-written manifest helper, and malformed
  lock records stop removal before directory deletion.
- `orhun/dil.oh` provides reusable Orhun-source language-development helpers:
  token records, token cursors, expected-token diagnostics, AST node builders,
  token/value summaries, diagnostic-message summaries, and small AST summaries
  for compiler/DSL prototypes written in Orhun. Its diagnostic records can be
  rendered as consistent code and source-location messages for beginner-facing
  DSLs and editor tooling, with optional source-line and column-marker output.

## Main Remaining Work

- Stabilize the language specification and migration policy.
- Keep growing parser parity until the Orhun parser can replace more of the C++
  parser path.
- Grow compiler parity beyond the current test corpus and reduce the remaining
  C++ serialization/runtime bridge behind the portable Orhun compiler CLI.
- Add platform code-signing and installer signing to versioned releases.
- Add native platform installer formats and signing on top of the verified
  cross-platform compiler/runtime archive installer.
- Strengthen package manager UX, security checks, lockfile behavior, and docs.
- Grow the Orhun-source language toolkit into shared lexer/parser/compiler
  building blocks for Orhun itself and for new small languages written in Orhun.
- Add beginner learning material and larger example projects.
- Harden the existing representative-workload performance gates with retained
  baselines and stricter release-candidate regression budgets.
- Keep compatibility and deprecation rules credible before 1.0 and especially
  before 2.1.0.

## 2.1.0 Rule

Do not call Orhun `2.1.0` just because the number looks mature. `2.1.0` should
mean users can start real projects with reasonable confidence. The gates in
`docs/VERSIONING.md` must be met first.
