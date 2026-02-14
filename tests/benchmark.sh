#!/usr/bin/env bash
set -euo pipefail

COMPILER="${1:-g++}"
OUTPUT="${2:-orhun_bench}"
TEKRAR="${3:-30}"
JSON_OUT="${4:-benchmark_results.jsonl}"
BASELINE="${5:-}"
GATE_P50="${6:-0}"
GATE_P90="${7:-0}"
OLCUM_MODU="${8:-runtime}"
WARMUP="${9:-10}"
GATE_MODE="${10:-suite}"

if [[ ! -f "${OUTPUT}" ]]; then
  echo "[build] ${OUTPUT} bulunamadi, derleniyor..."
  "${COMPILER}" -std=c++17 -Wall -Wextra -pedantic \
    main.cpp Lexer.cpp Parser.cpp Interpreter.cpp Chunk.cpp Compiler.cpp VM.cpp \
    -o "${OUTPUT}"
fi

cases=(
  "tests/cases/basic_math.oh"
  "tests/cases/assignment_equals.oh"
  "tests/cases/while_float.oh"
  "tests/cases/list_comprehension.oh"
  "tests/cases/oop_super.oh"
  "tests/cases/json_parse.oh"
  "tests/cases/f_string.oh"
  "tests/cases/f_string_escape.oh"
  "tests/cases/slicing.oh"
  "tests/cases/dict_nested.oh"
  "tests/cases/try_break_continue.oh"
  "tests/cases/try_catch_runtime.oh"
  "tests/cases/module_stdlib.oh"
  "tests/cases/stdlib_modules.oh"
  "tests/cases/stdlib_database.oh"
  "tests/cases/stdlib_regex_date.oh"
  "tests/cases/stdlib_async.oh"
  "tests/cases/vm_loop_control.oh"
)

rm -f "${JSON_OUT}"
echo "[bench] Orhun hiz karsilastirma (JSONL: ${JSON_OUT})"
for src in "${cases[@]}"; do
  echo ""
  echo "=== ${src} ==="
  cmd=("./${OUTPUT}" hiz "${src}" "--tekrar=${TEKRAR}" "--warmup=${WARMUP}" "--olcum-modu=${OLCUM_MODU}" --json)
  if [[ -n "${BASELINE}" ]]; then
    cmd+=("--baseline" "${BASELINE}")
  fi
  if ! json="$("${cmd[@]}" 2>&1)"; then
    echo "[skip] ${src} benchmark atlandi (VM destek disi olabilir)."
  else
    echo "${json}" | tr -d '\r' >> "${JSON_OUT}"
    echo "${json}"
  fi
done

if [[ "${GATE_P50}" != "0" || "${GATE_P90}" != "0" ]]; then
  echo ""
  echo "[gate] KPI kontrolu"
  ./tests/benchmark_gate.sh "${JSON_OUT}" "${GATE_P50}" "${GATE_P90}" "${GATE_MODE}"
fi
