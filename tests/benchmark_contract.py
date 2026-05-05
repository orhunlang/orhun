#!/usr/bin/env python3
import argparse
import json
import subprocess
import tempfile
from pathlib import Path


def run_cmd(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def parse_last_json(stdout: str) -> dict:
    lines = [line.strip() for line in stdout.splitlines() if line.strip()]
    if not lines:
        raise RuntimeError("benchmark json output is empty")
    return json.loads(lines[-1])


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> int:
    parser = argparse.ArgumentParser(description="Orhun benchmark contract test")
    parser.add_argument("binary", help="Orhun executable path")
    args = parser.parse_args()

    binary = Path(args.binary)
    if not binary.exists():
        raise SystemExit(f"Binary not found: {binary}")

    with tempfile.TemporaryDirectory(prefix="orhun_bench_contract_") as tmp:
        src = Path(tmp) / "mini.oh"
        src.write_text("yazdır 1 + 1\n", encoding="utf-8")

        for mode in ("runtime", "full"):
            proc = run_cmd(
                [
                    str(binary),
                    "hiz",
                    str(src),
                    "--tekrar=2",
                    "--warmup=1",
                    f"--olcum-modu={mode}",
                    "--json",
                ]
            )
            require(
                proc.returncode == 0,
                f"hiz failed for mode={mode}: rc={proc.returncode} stderr={proc.stderr}",
            )
            payload = parse_last_json(proc.stdout)
            for key in ("dosya", "tekrar", "warmup", "olcum_modu", "parse_ms", "vm_compile_ms", "gate_result", "hizlanma"):
                require(key in payload, f"missing key in benchmark json: {key}")
            require(payload["olcum_modu"] == mode, f"olcum_modu mismatch: {payload['olcum_modu']} != {mode}")
            require(payload["warmup"] == 1, f"warmup mismatch: {payload['warmup']}")
            require(payload["gate_result"] in ("pass", "fail"), "gate_result must be pass/fail")
            require(
                isinstance(payload["parse_ms"], (int, float))
                and isinstance(payload["vm_compile_ms"], (int, float)),
                "parse_ms/vm_compile_ms must be numeric",
            )

        invalid_mode = run_cmd(
            [
                str(binary),
                "hiz",
                str(src),
                "--tekrar=1",
                "--warmup=1",
                "--olcum-modu=invalid",
                "--json",
            ]
        )
        require(invalid_mode.returncode == 1, "invalid mode must fail with rc=1")

        gate_fail = run_cmd(
            [
                str(binary),
                "hiz",
                str(src),
                "--tekrar=2",
                "--warmup=0",
                "--olcum-modu=runtime",
                "--json",
                "--gate-p50=999",
                "--gate-p90=999",
            ]
        )
        require(gate_fail.returncode == 2, "gate fail must return rc=2")

        infra_fail = run_cmd(
            [
                str(binary),
                "hiz",
                str(src),
                "--tekrar=1",
                "--warmup=0",
                "--olcum-modu=runtime",
                "--json",
                "--baseline",
                str(Path(tmp) / "missing_baseline.jsonl"),
            ]
        )
        require(infra_fail.returncode == 3, "infrastructure fail must return rc=3")

    print("Benchmark contract passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
