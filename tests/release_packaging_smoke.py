#!/usr/bin/env python3
import hashlib
import json
import subprocess
import sys
import tarfile
import tempfile
import zipfile
from pathlib import Path


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def run(repo: Path, *args: str, expected: int = 0) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        [sys.executable, "tools/release_package.py", *args],
        cwd=repo,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    require(
        proc.returncode == expected,
        f"Command returned {proc.returncode}, expected {expected}:\n{proc.stdout}\n{proc.stderr}",
    )
    return proc


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_installer(
    repo: Path, *args: str, expected: int = 0
) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        [sys.executable, "tools/install_compiler.py", *args],
        cwd=repo,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    require(
        proc.returncode == expected,
        f"Installer returned {proc.returncode}, expected {expected}:\n"
        f"{proc.stdout}\n{proc.stderr}",
    )
    return proc


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    version = (repo / "VERSION").read_text(encoding="utf-8").strip()
    workflow = (repo / ".github" / "workflows" / "release.yml").read_text(
        encoding="utf-8"
    )
    for fragment in (
        'tags: ["v*.*.*"]',
        "tests/roadmap_smoke.py",
        "tools/release_package.py create",
        "tools/release_package.py create-runtime",
        "tools/install_compiler.py",
        "actions/attest@v4",
        "id-token: write",
        "attestations: write",
        "artifact-metadata: write",
        "gh release create",
    ):
        require(fragment in workflow, f"Release workflow missing contract: {fragment}")

    with tempfile.TemporaryDirectory(prefix="orhun_release_smoke_") as raw_temp:
        temp = Path(raw_temp)
        bundle = temp / "bundle"
        (bundle / "StdLib" / "orhun").mkdir(parents=True)
        (bundle / "bootstrap-compiler.manifest.json").write_text(
            '{"format":"ORHUN-COMPILER-BUNDLE-1"}\n', encoding="utf-8"
        )
        (bundle / "StdLib" / "bootstrap.manifest.json").write_text(
            '{"format":"ORHUN-BOOTSTRAP-1"}\n', encoding="utf-8"
        )
        (bundle / "StdLib" / "orhun" / "derleyici.obc").write_bytes(b"ORH-OBC\x00")
        executable = bundle / "orhun-derleyici"
        executable.write_bytes(b"release-smoke")
        executable.chmod(0o755)

        runtime_bundle = temp / "runtime-bundle"
        (runtime_bundle / "StdLib" / "orhun").mkdir(parents=True)
        runtime_executable = runtime_bundle / "orhun"
        runtime_executable.write_bytes(b"runtime-smoke")
        runtime_executable.chmod(0o755)
        (runtime_bundle / "StdLib" / "orhun" / "temel.oh").write_text(
            'surum olsun "smoke"\n', encoding="utf-8"
        )
        (runtime_bundle / "VERSION").write_text(version + "\n", encoding="utf-8")
        (runtime_bundle / "LICENSE").write_text("test license\n", encoding="utf-8")
        (runtime_bundle / "README.md").write_text("test readme\n", encoding="utf-8")

        outputs = []
        for attempt in ("first", "second"):
            output = temp / attempt
            run(
                repo,
                "create",
                "--bundle",
                str(bundle),
                "--output",
                str(output),
                "--platform",
                "linux-x86_64",
                "--tag",
                f"v{version}",
            )
            outputs.append(output / f"orhun-compiler-{version}-linux-x86_64.tar.gz")

        require(
            outputs[0].read_bytes() == outputs[1].read_bytes(),
            "Repeated tar.gz release archives must be byte-identical",
        )
        with tarfile.open(outputs[0], "r:gz") as archive:
            members = archive.getnames()
        require(members, "tar.gz release archive is empty")
        require(
            all(name.startswith(f"orhun-compiler-{version}-linux-x86_64/") for name in members),
            "tar.gz members must share the versioned release root",
        )

        runtime_archives = []
        for attempt in ("runtime-first", "runtime-second"):
            runtime_output = temp / attempt
            run(
                repo,
                "create-runtime",
                "--bundle",
                str(runtime_bundle),
                "--output",
                str(runtime_output),
                "--platform",
                "linux-x86_64",
                "--tag",
                f"v{version}",
            )
            runtime_archives.append(
                runtime_output / f"orhun-runtime-{version}-linux-x86_64.tar.gz"
            )
        require(
            runtime_archives[0].read_bytes() == runtime_archives[1].read_bytes(),
            "Repeated runtime release archives must be byte-identical",
        )
        with tarfile.open(runtime_archives[0], "r:gz") as archive:
            runtime_members = archive.getnames()
        require(
            all(
                name.startswith(f"orhun-runtime-{version}-linux-x86_64/")
                for name in runtime_members
            ),
            "Runtime archive members must share the versioned release root",
        )

        windows_archives = []
        for attempt in ("windows-first", "windows-second"):
            windows_output = temp / attempt
            run(
                repo,
                "create",
                "--bundle",
                str(bundle),
                "--output",
                str(windows_output),
                "--platform",
                "Windows-X64",
                "--tag",
                f"v{version}",
            )
            windows_archives.append(
                windows_output / f"orhun-compiler-{version}-windows-x64.zip"
            )
        require(
            windows_archives[0].read_bytes() == windows_archives[1].read_bytes(),
            "Repeated zip release archives must be byte-identical",
        )
        windows_archive = windows_archives[0]
        with zipfile.ZipFile(windows_archive) as archive:
            members = archive.namelist()
        require(members, "zip release archive is empty")
        require(
            all(name.startswith(f"orhun-compiler-{version}-windows-x64/") for name in members),
            "zip members must share the versioned release root",
        )

        if sys.platform == "win32":
            host_archive = windows_archive
        elif sys.platform == "darwin":
            macos_output = temp / "macos-host"
            run(
                repo,
                "create",
                "--bundle",
                str(bundle),
                "--output",
                str(macos_output),
                "--platform",
                "macos-x64",
                "--tag",
                f"v{version}",
            )
            host_archive = (
                macos_output / f"orhun-compiler-{version}-macos-x64.tar.gz"
            )
        else:
            host_archive = outputs[0]

        combined = temp / "combined"
        combined.mkdir()
        for archive in (outputs[0], windows_archive, runtime_archives[0]):
            (combined / archive.name).write_bytes(archive.read_bytes())
        checksum_manifest = combined / "SHA256SUMS"
        run(
            repo,
            "checksums",
            "--directory",
            str(combined),
            "--output",
            str(checksum_manifest),
        )
        checksum_text = checksum_manifest.read_text(encoding="ascii")
        require(
            f"{digest(outputs[0])}  {outputs[0].name}" in checksum_text,
            "Combined checksums missing tar.gz archive",
        )
        require(
            f"{digest(windows_archive)}  {windows_archive.name}" in checksum_text,
            "Combined checksums missing zip archive",
        )
        require(
            f"{digest(runtime_archives[0])}  {runtime_archives[0].name}"
            in checksum_text,
            "Combined checksums missing runtime archive",
        )

        install_root = temp / "installed-compiler"
        installed = run_installer(
            repo,
            str(outputs[0]),
            "--install-root",
            str(install_root),
            "--no-shim",
            "--allow-cross-platform",
            "--json",
        )
        install_payload = json.loads(installed.stdout.strip().splitlines()[-1])
        require(
            install_payload["format"] == "orhun-compiler-install-v1",
            "Installer result format changed",
        )
        require(
            install_payload["version"] == version,
            "Installer result version changed",
        )
        require(
            (install_root / "orhun-derleyici").read_bytes() == b"release-smoke",
            "Installer did not publish the compiler executable",
        )
        run_installer(
            repo,
            str(outputs[0]),
            "--install-root",
            str(install_root),
            "--no-shim",
            "--allow-cross-platform",
            expected=1,
        )
        run_installer(
            repo,
            str(outputs[0]),
            "--install-root",
            str(install_root),
            "--no-shim",
            "--allow-cross-platform",
            "--force",
        )

        shim_install_root = temp / "shim-installed-compiler"
        bin_dir = temp / "bin"
        shim_result = run_installer(
            repo,
            str(host_archive),
            "--install-root",
            str(shim_install_root),
            "--bin-dir",
            str(bin_dir),
            "--json",
        )
        shim_payload = json.loads(shim_result.stdout.strip().splitlines()[-1])
        shim = Path(shim_payload["shim"])
        require(
            shim.exists() or shim.is_symlink(),
            "Installer did not create the compiler command shim",
        )

        unrelated = temp / "unrelated-directory"
        unrelated.mkdir()
        (unrelated / "keep.txt").write_text("keep", encoding="utf-8")
        run_installer(
            repo,
            str(outputs[0]),
            "--install-root",
            str(unrelated),
            "--no-shim",
            "--allow-cross-platform",
            "--force",
            expected=1,
        )
        require(
            (unrelated / "keep.txt").read_text(encoding="utf-8") == "keep",
            "Installer replaced an unrelated directory",
        )

        foreign_archive = outputs[0] if sys.platform == "win32" else windows_archive
        foreign_install = temp / "foreign-install"
        run_installer(
            repo,
            str(foreign_archive),
            "--install-root",
            str(foreign_install),
            "--no-shim",
            expected=1,
        )
        require(
            not foreign_install.exists(),
            "Foreign-platform archive must require explicit opt-in",
        )

        corrupt = temp / outputs[0].name
        corrupt.write_bytes(outputs[0].read_bytes() + b"tampered")
        corrupt.with_name(corrupt.name + ".sha256").write_text(
            f"{digest(outputs[0])}  {corrupt.name}\n",
            encoding="ascii",
        )
        corrupt_install = temp / "corrupt-install"
        run_installer(
            repo,
            str(corrupt),
            "--install-root",
            str(corrupt_install),
            "--no-shim",
            expected=1,
        )
        require(not corrupt_install.exists(), "Tampered archive must not be installed")

        malicious = temp / "malicious.zip"
        with zipfile.ZipFile(malicious, "w") as archive:
            archive.writestr("../escaped.txt", b"unsafe")
        malicious.with_name(malicious.name + ".sha256").write_text(
            f"{digest(malicious)}  {malicious.name}\n",
            encoding="ascii",
        )
        run_installer(
            repo,
            str(malicious),
            "--install-root",
            str(temp / "malicious-install"),
            "--no-shim",
            expected=1,
        )
        require(not (temp / "escaped.txt").exists(), "Installer allowed archive traversal")

        wrong_tag = subprocess.run(
            [
                sys.executable,
                "tools/release_package.py",
                "create",
                "--bundle",
                str(bundle),
                "--output",
                str(temp / "wrong-tag"),
                "--platform",
                "linux-x86_64",
                "--tag",
                "v999.0.0",
            ],
            cwd=repo,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        require(wrong_tag.returncode != 0, "Mismatched release tag must be rejected")
        require("must exactly match" in wrong_tag.stderr, "Wrong-tag error must be clear")

    print(
        "Release packaging smoke passed "
        "(deterministic compiler/runtime archives, checksums, secure installer, "
        "tag gate, provenance workflow)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
