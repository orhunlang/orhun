#!/usr/bin/env python3
import argparse
import hashlib
import json
import tempfile
import zlib
from pathlib import Path

from compiler_prototype_smoke import require, run_cmd


def combined(proc) -> str:
    return (proc.stdout + proc.stderr).replace("\r\n", "\n")


def write_metadata(path: Path, metadata: dict) -> None:
    path.write_text(
        json.dumps(metadata, ensure_ascii=False),
        encoding="utf-8",
        newline="\n",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify OBC metadata integrity")
    parser.add_argument("binary", help="Orhun executable path")
    args = parser.parse_args()

    repo = Path(__file__).resolve().parents[1]
    binary = Path(args.binary).resolve()
    require(binary.exists(), f"Binary not found: {binary}")

    with tempfile.TemporaryDirectory(prefix="orhun_obc_metadata_") as tmp:
        tmpdir = Path(tmp)
        source = tmpdir / "metadata.oh"
        source.write_text('yazdır "metadata"\n', encoding="utf-8", newline="\n")
        output = tmpdir / "metadata_artifact"
        compiled = run_cmd([str(binary), "derle", str(source), str(output)], repo)
        require(
            compiled.returncode == 0,
            f"metadata fixture compile failed: {combined(compiled)}",
        )

        obc = output.with_suffix(".obc")
        metadata_path = output.with_suffix(".obc.meta.json")
        payload = obc.read_bytes()
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        require(
            metadata.get("format") == "orhun-obc-v2"
            and metadata.get("payload_size") == len(payload)
            and metadata.get("payload_crc32")
            == f"{zlib.crc32(payload) & 0xFFFFFFFF:08x}"
            and metadata.get("payload_sha256") == hashlib.sha256(payload).hexdigest()
            and metadata.get("source_name") == source.name,
            f"generated OBC v2 metadata contract mismatch: {metadata}",
        )

        verified = run_cmd([str(binary), "obc-dogrula", str(obc)], repo)
        require(
            verified.returncode == 0
            and "OBC artifact dogrulandi:" in combined(verified),
            f"default OBC metadata verification failed: {combined(verified)}",
        )

        v1_metadata = dict(metadata)
        v1_metadata["format"] = "orhun-obc-v1"
        v1_metadata.pop("payload_sha256")
        v1_path = tmpdir / "legacy-v1.meta.json"
        write_metadata(v1_path, v1_metadata)
        verified_v1 = run_cmd(
            [str(binary), "obc-verify", str(obc), str(v1_path)],
            repo,
        )
        require(
            verified_v1.returncode == 0,
            f"legacy OBC v1 metadata must remain verifiable: {combined(verified_v1)}",
        )

        bad_sha = dict(metadata)
        bad_sha["payload_sha256"] = "0" * 64
        bad_sha_path = tmpdir / "bad-sha.meta.json"
        write_metadata(bad_sha_path, bad_sha)
        rejected_sha = run_cmd(
            [str(binary), "obc-dogrula", str(obc), str(bad_sha_path)],
            repo,
        )
        require(
            rejected_sha.returncode != 0
            and "payload SHA256 uyusmuyor" in combined(rejected_sha),
            "OBC verifier must reject a mismatched SHA256",
        )

        bad_crc = dict(metadata)
        bad_crc["payload_crc32"] = "00000000"
        bad_crc_path = tmpdir / "bad-crc.meta.json"
        write_metadata(bad_crc_path, bad_crc)
        rejected_crc = run_cmd(
            [str(binary), "obc-dogrula", str(obc), str(bad_crc_path)],
            repo,
        )
        require(
            rejected_crc.returncode != 0
            and "payload CRC32 uyusmuyor" in combined(rejected_crc),
            "OBC verifier must reject a mismatched CRC32",
        )

        bad_size = dict(metadata)
        bad_size["payload_size"] = len(payload) + 1
        bad_size_path = tmpdir / "bad-size.meta.json"
        write_metadata(bad_size_path, bad_size)
        rejected_size = run_cmd(
            [str(binary), "obc-dogrula", str(obc), str(bad_size_path)],
            repo,
        )
        require(
            rejected_size.returncode != 0
            and "payload boyutu uyusmuyor" in combined(rejected_size),
            "OBC verifier must reject a mismatched payload size",
        )

    print(
        "OBC metadata smoke passed (v2 SHA256 contract, v1 compatibility, "
        "size/CRC32/SHA256 rejection)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
