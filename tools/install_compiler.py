#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import sys
import tarfile
import tempfile
import zipfile
from pathlib import Path, PurePosixPath


ROOT_RE = re.compile(
    r"^orhun-compiler-"
    r"(?P<version>(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)"
    r"(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?)"
    r"-(?P<platform>(?:windows|linux|macos)-[a-z0-9][a-z0-9._-]*)$"
)
MAX_ARCHIVE_ENTRIES = 4096
MAX_UNCOMPRESSED_BYTES = 512 * 1024 * 1024


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_checksum(archive: Path, checksum_file: Path) -> str:
    require(checksum_file.is_file(), f"Checksum file not found: {checksum_file}")
    matches = []
    for raw_line in checksum_file.read_text(encoding="ascii").splitlines():
        parts = raw_line.strip().split()
        if len(parts) != 2:
            continue
        digest, name = parts
        name = name.removeprefix("*")
        if name == archive.name:
            matches.append(digest.lower())

    require(
        len(matches) == 1,
        f"Checksum file must contain exactly one entry for {archive.name}",
    )
    expected = matches[0]
    require(
        re.fullmatch(r"[0-9a-f]{64}", expected) is not None,
        "Checksum entry is not a SHA-256 digest",
    )
    actual = sha256(archive)
    require(actual == expected, f"SHA-256 mismatch for {archive.name}")
    return actual


def safe_parts(raw_name: str) -> tuple[str, ...]:
    normalized = raw_name.replace("\\", "/")
    path = PurePosixPath(normalized)
    require(not path.is_absolute(), f"Archive contains absolute path: {raw_name}")
    require(".." not in path.parts, f"Archive contains parent traversal: {raw_name}")
    parts = tuple(part for part in path.parts if part not in ("", "."))
    require(parts, f"Archive contains empty path: {raw_name}")
    require(
        all("\x00" not in part and ":" not in part for part in parts),
        f"Archive contains unsafe path component: {raw_name}",
    )
    return parts


def register_entry(
    raw_name: str,
    parts: tuple[str, ...],
    size: int,
    seen: set[str],
    totals: list[int],
) -> None:
    require(totals[0] < MAX_ARCHIVE_ENTRIES, "Archive contains too many entries")
    require(size >= 0, f"Archive entry has invalid size: {raw_name}")
    require(
        totals[1] + size <= MAX_UNCOMPRESSED_BYTES,
        "Archive uncompressed size exceeds the installer limit",
    )
    key = "/".join(parts).casefold()
    require(key not in seen, f"Archive contains duplicate path: {raw_name}")
    seen.add(key)
    totals[0] += 1
    totals[1] += size


def write_file(destination: Path, data: bytes, mode: int) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(data)
    if os.name != "nt":
        destination.chmod(0o755 if mode & 0o111 else 0o644)


def extract_zip(archive_path: Path, destination: Path) -> None:
    seen: set[str] = set()
    totals = [0, 0]
    with zipfile.ZipFile(archive_path) as archive:
        for info in archive.infolist():
            parts = safe_parts(info.filename)
            register_entry(info.filename, parts, info.file_size, seen, totals)
            target = destination.joinpath(*parts)
            mode = info.external_attr >> 16
            require(not stat.S_ISLNK(mode), f"Archive contains symbolic link: {info.filename}")
            if info.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            require(
                stat.S_IFMT(mode) in (0, stat.S_IFREG),
                f"Archive contains unsupported entry: {info.filename}",
            )
            write_file(target, archive.read(info), mode)


def extract_tar(archive_path: Path, destination: Path) -> None:
    seen: set[str] = set()
    totals = [0, 0]
    with tarfile.open(archive_path, "r:gz") as archive:
        for member in archive:
            parts = safe_parts(member.name)
            register_entry(member.name, parts, member.size, seen, totals)
            target = destination.joinpath(*parts)
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            require(member.isfile(), f"Archive contains unsupported entry: {member.name}")
            handle = archive.extractfile(member)
            require(handle is not None, f"Could not read archive entry: {member.name}")
            write_file(target, handle.read(), member.mode)


def extract_archive(archive: Path, destination: Path) -> None:
    if archive.name.endswith(".zip"):
        extract_zip(archive, destination)
        return
    if archive.name.endswith(".tar.gz"):
        extract_tar(archive, destination)
        return
    raise RuntimeError("Compiler archive must end with .zip or .tar.gz")


def inspect_root(extracted: Path) -> tuple[Path, str, str, Path]:
    entries = list(extracted.iterdir())
    require(
        len(entries) == 1 and entries[0].is_dir(),
        "Compiler archive must contain exactly one top-level directory",
    )
    root = entries[0]
    match = ROOT_RE.fullmatch(root.name)
    require(match is not None, f"Unexpected compiler archive root: {root.name}")
    require(
        (root / "bootstrap-compiler.manifest.json").is_file(),
        "Compiler archive is missing bootstrap-compiler.manifest.json",
    )
    require(
        (root / "StdLib" / "bootstrap.manifest.json").is_file(),
        "Compiler archive is missing StdLib/bootstrap.manifest.json",
    )
    executable = root / ("orhun-derleyici.exe" if (root / "orhun-derleyici.exe").is_file() else "orhun-derleyici")
    require(executable.is_file(), "Compiler archive is missing orhun-derleyici")
    return root, match.group("version"), match.group("platform"), executable


def default_install_root(version: str) -> Path:
    if os.name == "nt":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
        return base / "Orhun" / "compiler" / version
    return Path.home() / ".local" / "share" / "orhun" / "compiler" / version


def default_bin_dir() -> Path:
    if os.name == "nt":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
        return base / "Orhun" / "bin"
    return Path.home() / ".local" / "bin"


def host_os_name() -> str:
    if os.name == "nt":
        return "windows"
    if sys.platform == "darwin":
        return "macos"
    return "linux"


def publish_tree(source: Path, destination: Path, force: bool) -> None:
    require(
        destination != Path(destination.anchor),
        f"Refusing to install over filesystem root: {destination}",
    )
    destination_present = destination.exists() or destination.is_symlink()
    if destination_present:
        require(force, f"Install root already exists: {destination}")
        require(
            destination.is_dir()
            and not destination.is_symlink()
            and (destination / "bootstrap-compiler.manifest.json").is_file(),
            f"Refusing to replace non-Orhun install root: {destination}",
        )

    destination.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix=".orhun-install-", dir=destination.parent) as raw:
        staged = Path(raw) / destination.name
        shutil.copytree(source, staged)
        backup = destination.with_name(destination.name + ".previous")
        require(
            not backup.exists() and not backup.is_symlink(),
            f"Previous install backup already exists: {backup}",
        )
        if destination_present:
            destination.replace(backup)
        try:
            staged.replace(destination)
        except Exception:
            if backup.exists() and not destination.exists():
                backup.replace(destination)
            raise
        if backup.exists():
            shutil.rmtree(backup)


def create_shim(executable: Path, bin_dir: Path, force: bool) -> Path:
    bin_dir.mkdir(parents=True, exist_ok=True)
    if os.name == "nt":
        shim = bin_dir / "orhun-derleyici.cmd"
        require(force or not shim.exists(), f"Compiler shim already exists: {shim}")
        shim.write_text(f'@"{executable}" %*\r\n', encoding="utf-8", newline="")
        return shim

    shim = bin_dir / "orhun-derleyici"
    require(force or not shim.exists(), f"Compiler shim already exists: {shim}")
    if shim.exists() or shim.is_symlink():
        shim.unlink()
    shim.symlink_to(executable)
    return shim


def install(args: argparse.Namespace) -> int:
    archive = args.archive.resolve()
    require(archive.is_file(), f"Compiler archive not found: {archive}")
    checksum_file = (
        args.checksum.resolve()
        if args.checksum is not None
        else archive.with_name(archive.name + ".sha256")
    )
    digest = verify_checksum(archive, checksum_file)

    with tempfile.TemporaryDirectory(prefix="orhun-compiler-extract-") as raw:
        extracted = Path(raw)
        extract_archive(archive, extracted)
        root, version, platform_name, source_executable = inspect_root(extracted)
        require(
            args.allow_cross_platform or platform_name.split("-", 1)[0] == host_os_name(),
            f"Archive platform {platform_name} does not match host {host_os_name()}",
        )
        install_root = (
            args.install_root.expanduser().resolve()
            if args.install_root is not None
            else default_install_root(version).resolve()
        )
        executable_name = source_executable.name
        publish_tree(root, install_root, args.force)

    installed_executable = install_root / executable_name
    shim = None
    if not args.no_shim:
        bin_dir = (
            args.bin_dir.expanduser().resolve()
            if args.bin_dir is not None
            else default_bin_dir().resolve()
        )
        shim = create_shim(installed_executable, bin_dir, args.force)

    result = {
        "format": "orhun-compiler-install-v1",
        "version": version,
        "platform": platform_name,
        "sha256": digest,
        "install_root": str(install_root),
        "executable": str(installed_executable),
        "shim": str(shim) if shim is not None else None,
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
    else:
        print(f"Orhun compiler {version} installed: {install_root}")
        if shim is not None:
            print(f"Command shim: {shim}")
            print(f"Ensure this directory is on PATH: {shim.parent}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify and install an extracted Orhun compiler release archive"
    )
    parser.add_argument("archive", type=Path, help="Downloaded .zip or .tar.gz archive")
    parser.add_argument(
        "--checksum",
        type=Path,
        help="SHA-256 sidecar; defaults to <archive>.sha256",
    )
    parser.add_argument("--install-root", type=Path, help="Destination compiler directory")
    parser.add_argument("--bin-dir", type=Path, help="Directory for command shim")
    parser.add_argument("--no-shim", action="store_true", help="Do not create a command shim")
    parser.add_argument(
        "--allow-cross-platform",
        action="store_true",
        help="Allow staging a compiler archive for another operating system",
    )
    parser.add_argument("--force", action="store_true", help="Replace an existing installation")
    parser.add_argument("--json", action="store_true", help="Print machine-readable result")
    return parser.parse_args()


def main() -> int:
    return install(parse_args())


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, OSError, tarfile.TarError, zipfile.BadZipFile) as error:
        print(f"Hata: {error}", file=sys.stderr)
        raise SystemExit(1)
