#!/usr/bin/env python3
import json
import os
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


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def gate_args(jsonl: Path, mode: str, min_p50: float, min_p90: float) -> list[str]:
    if os.name == "nt":
        return [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            "tests/benchmark_gate.ps1",
            "-JsonL",
            str(jsonl),
            "-MinP50",
            str(min_p50),
            "-MinP90",
            str(min_p90),
            "-Mode",
            mode,
        ]
    return [
        "bash",
        "tests/benchmark_gate.sh",
        str(jsonl),
        str(min_p50),
        str(min_p90),
        mode,
    ]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="orhun_bench_pipeline_") as tmp:
        jsonl = Path(tmp) / "results.jsonl"
        rows = [
            {
                "dosya": "tests/cases/a.oh",
                "hizlanma": {"p50_x": 1.60, "p90_x": 1.40},
                "gate": {"p50_oran": 1.60, "p90_oran": 1.40},
            },
            {
                "dosya": "tests/cases/b.oh",
                "hizlanma": {"p50_x": 1.10, "p90_x": 1.20},
                "gate": {"p50_oran": 1.10, "p90_oran": 1.20},
            },
        ]
        jsonl.write_text(
            "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n",
            encoding="utf-8",
        )

        suite_pass = run_cmd(gate_args(jsonl, "suite", 1.2, 1.2))
        require(
            suite_pass.returncode == 0,
            f"suite mode expected rc=0, got {suite_pass.returncode}\n{suite_pass.stdout}\n{suite_pass.stderr}",
        )

        per_case_fail = run_cmd(gate_args(jsonl, "per_case", 1.2, 1.2))
        require(
            per_case_fail.returncode == 2,
            f"per_case mode expected rc=2, got {per_case_fail.returncode}\n{per_case_fail.stdout}\n{per_case_fail.stderr}",
        )

        missing = run_cmd(gate_args(Path(tmp) / "missing.jsonl", "suite", 1.2, 1.2))
        require(
            missing.returncode == 3,
            f"missing jsonl expected rc=3, got {missing.returncode}\n{missing.stdout}\n{missing.stderr}",
        )

    print("Benchmark pipeline smoke passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
