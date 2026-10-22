#!/usr/bin/env bash
set -euo pipefail

COMPILER="${1:-g++}"
OUTPUT="${2:-build/orhun_bench}"
TEKRAR="${3:-30}"
JSON_OUT="${4:-build/benchmark_results.jsonl}"
BASELINE="${5:-}"
GATE_P50="${6:-0}"
GATE_P90="${7:-0}"
OLCUM_MODU="${8:-runtime}"
WARMUP="${9:-10}"
GATE_MODE="${10:-suite}"
GATE_BASELINE="${11:-}"
GATE_BASELINE_P50_RATIO="${12:-0}"
GATE_BASELINE_P90_RATIO="${13:-0}"

mkdir -p "$(dirname "${OUTPUT}")"
mkdir -p "$(dirname "${JSON_OUT}")"

if [[ ! -f "${OUTPUT}" ]]; then
  echo "[build] ${OUTPUT} bulunamadi, derleniyor..."
  "${COMPILER}" -std=c++17 -O2 -DNDEBUG -Wall -Wextra -pedantic \
    main.cpp Lexer.cpp Parser.cpp Interpreter.cpp Chunk.cpp Compiler.cpp VM.cpp \
    -o "${OUTPUT}"
fi

bench_manifest="tests/benchmarks/python_compare/benchmarks.txt"
if [[ ! -f "${bench_manifest}" ]]; then
  echo "Benchmark manifest dosyasi bulunamadi: ${bench_manifest}"
  exit 3
fi
cases=()
bench=""
case_count=0
while IFS= read -r bench || [[ -n "${bench}" ]]; do
  bench="${bench%$'\r'}"
  [[ -z "${bench}" || "${bench}" == \#* ]] && continue
  cases+=("tests/benchmarks/python_compare/${bench}.oh")
  case_count=$((case_count + 1))
done < "${bench_manifest}"
if [[ "${case_count}" -eq 0 ]]; then
  echo "Benchmark manifest dosyasi bos: ${bench_manifest}"
  exit 3
fi

rm -f "${JSON_OUT}"
ok_count=0
failed=0
echo "[bench] Orhun hiz karsilastirma (JSONL: ${JSON_OUT})"
for src in "${cases[@]}"; do
  echo ""
  echo "=== ${src} ==="
  cmd=("./${OUTPUT}" hiz "${src}" "--tekrar=${TEKRAR}" "--warmup=${WARMUP}" "--olcum-modu=${OLCUM_MODU}" --json)
  if [[ -n "${BASELINE}" ]]; then
    cmd+=("--baseline" "${BASELINE}")
  fi
  if ! json="$("${cmd[@]}" 2>&1)"; then
    echo "[FAIL] ${src} benchmark basarisiz."
    [[ -n "${json}" ]] && echo "${json}"
    failed=1
  else
    echo "${json}" | tr -d '\r' >> "${JSON_OUT}"
    echo "${json}"
    ok_count=$((ok_count + 1))
  fi
done

if [[ "${failed}" -ne 0 ]]; then
  echo "Benchmark smoke basarisiz."
  exit 3
fi
if [[ ! -f "${JSON_OUT}" ]]; then
  echo "Benchmark smoke basarisiz: JSONL dosyasi uretilmedi: ${JSON_OUT}"
  exit 3
fi
line_count="$(grep -cve '^[[:space:]]*$' "${JSON_OUT}" || true)"
if [[ "${line_count}" -le 0 ]]; then
  echo "Benchmark smoke basarisiz: JSONL dosyasi bos: ${JSON_OUT}"
  exit 3
fi
echo "[bench] toplam_ok=${ok_count} satir=${line_count}"

if [[ "${GATE_P50}" != "0" || "${GATE_P90}" != "0" || "${GATE_BASELINE_P50_RATIO}" != "0" || "${GATE_BASELINE_P90_RATIO}" != "0" ]]; then
  echo ""
  echo "[gate] KPI kontrolu"
  ./tests/benchmark_gate.sh "${JSON_OUT}" "${GATE_P50}" "${GATE_P90}" "${GATE_MODE}" "${GATE_BASELINE}" "${GATE_BASELINE_P50_RATIO}" "${GATE_BASELINE_P90_RATIO}"
fi
