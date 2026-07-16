#!/usr/bin/env python3
import argparse
import json
import os
import subprocess
from pathlib import Path


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


VALID_CHANNELS = {"stable", "beta", "nightly", "dev"}
FALSE_VALUES = {"0", "false", "off", "hayir", "no"}


def expected_channel(env: dict[str, str]) -> str:
    channel = env.get("ORHUN_CHANNEL") or env.get("ORHUN_RELEASE_CHANNEL") or "stable"
    normalized = channel.lower()
    return normalized if normalized in VALID_CHANNELS else "stable"


def environment_flag(env: dict[str, str], name: str) -> bool:
    value = env.get(name, "")
    return bool(value) and value.lower() not in FALSE_VALUES


def expected_fallback(env: dict[str, str], channel: str) -> bool:
    value = env.get("ORHUN_VM_FALLBACK", "")
    if value:
        return value.lower() not in FALSE_VALUES
    return channel in {"beta", "nightly", "dev"}


def expected_ffi_policy(env: dict[str, str], channel: str) -> str:
    configured = env.get("ORHUN_FFI_POLICY", "").strip().lower()
    if configured in {"off", "allowlist", "full"}:
        return configured
    return "allowlist" if channel == "stable" else "full"


def run_doctor(binary: Path, env: dict[str, str]) -> dict:
    proc = subprocess.run(
        [str(binary), "doctor", "--json"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )
    require(proc.returncode in (0, 2), f"doctor returned unexpected rc={proc.returncode}")

    lines = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    require(lines, "doctor --json output is empty")
    try:
        payload = json.loads(lines[-1])
    except Exception as ex:
        raise RuntimeError(f"doctor --json is not valid JSON: {ex}") from ex
    require(isinstance(payload, dict), "doctor --json root must be an object")
    return payload


def validate_contract(payload: dict, repo: Path, env: dict[str, str]) -> None:
    channel = expected_channel(env)

    for key in (
        "version",
        "build",
        "commit",
        "channel",
        "layout",
        "executable",
        "sibling_stdlib_path",
        "fallback_default",
        "fallback_source",
        "ci_profiles",
        "security_mode",
        "checks",
        "status",
    ):
        require(key in payload, f"doctor json missing key: {key}")

    expected_version = (repo / "VERSION").read_text(encoding="utf-8").strip()
    require(payload.get("version") == expected_version, "doctor version should match VERSION")
    require(payload.get("channel") == channel, f"doctor channel should be {channel}")
    require(
        payload.get("fallback_default") is expected_fallback(env, channel),
        f"doctor fallback default should match the {channel} channel",
    )
    require(payload.get("layout") == "source_checkout", "repo doctor layout should be source_checkout")
    require(payload.get("status") == "ready", "repo doctor status should be ready")
    require(isinstance(payload.get("executable"), str), "doctor executable should be a string")
    require(
        isinstance(payload.get("sibling_stdlib_path"), str),
        "doctor sibling_stdlib_path should be a string",
    )

    profiles = payload.get("ci_profiles")
    require(isinstance(profiles, list), "ci_profiles must be a list")
    for profile in ("ci", "nightly"):
        require(profile in profiles, f"ci_profiles missing {profile}")

    sec = payload.get("security_mode", {})
    require(isinstance(sec, dict), "security_mode must be an object")
    require(
        sec.get("ffi_policy_default") == expected_ffi_policy(env, channel),
        f"FFI policy should match the {channel} channel",
    )
    restricted = not (
        environment_flag(env, "ORHUN_UNSAFE")
        or environment_flag(env, "ORHUN_SYSTEM_UNSAFE")
    )
    require(
        sec.get("system_command_restricted_default") is restricted,
        "system command policy should match the environment",
    )
    require(
        sec.get("package_source_allowlist") is True,
        "package source allowlist should be enabled by default",
    )

    checks = payload.get("checks", {})
    require(isinstance(checks, dict), "checks must be an object")
    for key in (
        "runtime_executable",
        "source_checkout",
        "runtime_bundle",
        "sibling_stdlib",
        "compiler_files",
        "stdlib_core",
        "test_infra",
        "lsp_tools",
        "benchmark_gate_scripts",
        "git_access",
    ):
        require(isinstance(checks.get(key), bool), f"checks.{key} should be bool")
    require(checks.get("runtime_executable") is True, "doctor should find its executable")
    require(checks.get("source_checkout") is True, "repo should be a source checkout")


def main() -> int:
    parser = argparse.ArgumentParser(description="Doctor JSON contract smoke")
    parser.add_argument("binary", help="Orhun executable")
    args = parser.parse_args()

    binary = Path(args.binary)
    if not binary.exists():
        raise SystemExit(f"Binary not found: {binary}")
    repo = Path(__file__).resolve().parents[1]

    ambient_env = dict(os.environ)
    validate_contract(run_doctor(binary, ambient_env), repo, ambient_env)

    stable_env = ambient_env.copy()
    stable_env["ORHUN_CHANNEL"] = "stable"
    for name in (
        "ORHUN_RELEASE_CHANNEL",
        "ORHUN_VM_FALLBACK",
        "ORHUN_FFI_POLICY",
        "ORHUN_UNSAFE",
        "ORHUN_SYSTEM_UNSAFE",
    ):
        stable_env.pop(name, None)
    stable_payload = run_doctor(binary, stable_env)
    validate_contract(stable_payload, repo, stable_env)
    require(stable_payload.get("fallback_default") is False, "stable fallback default should be false")
    require(
        stable_payload.get("security_mode", {}).get("ffi_policy_default") == "allowlist",
        "stable FFI policy should default to allowlist",
    )

    print("Doctor JSON smoke passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
