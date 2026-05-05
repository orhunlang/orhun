#!/usr/bin/env bash
set -euo pipefail

COMPILER="${1:-g++}"
OUTPUT="${2:-build/orhun_cov}"
REPORT_DIR="${3:-coverage}"

mkdir -p "$(dirname "${OUTPUT}")"
mkdir -p "${REPORT_DIR}"

echo "[coverage] Building with instrumentation..."
"${COMPILER}" -std=c++17 -O0 -g --coverage -Wall -Wextra -pedantic \
  main.cpp Lexer.cpp Parser.cpp Interpreter.cpp Chunk.cpp Compiler.cpp VM.cpp \
  -o "${OUTPUT}"

echo "[coverage] Running test suite..."
./tests/run_tests.sh "${COMPILER}" "${OUTPUT}"

if command -v gcovr >/dev/null 2>&1; then
  echo "[coverage] Generating gcovr reports..."
  gcovr -r . --txt > "${REPORT_DIR}/summary.txt"
  gcovr -r . --xml-pretty -o "${REPORT_DIR}/coverage.xml"
  gcovr -r . --html --html-details -o "${REPORT_DIR}/index.html"
  cat "${REPORT_DIR}/summary.txt"
  summary_line="$(grep -E '^lines:' "${REPORT_DIR}/summary.txt" | head -n 1 || true)"
  if [[ -n "${summary_line}" ]]; then
    echo "[coverage] summary ${summary_line}"
  fi
else
  echo "[coverage] gcovr not found; falling back to gcov summary."
  gcov -o . main.cpp Lexer.cpp Parser.cpp Interpreter.cpp Chunk.cpp Compiler.cpp VM.cpp > "${REPORT_DIR}/gcov.txt" || true
  tail -n 20 "${REPORT_DIR}/gcov.txt" || true
  summary_line="$(grep -E 'Lines executed' "${REPORT_DIR}/gcov.txt" | head -n 1 || true)"
  if [[ -n "${summary_line}" ]]; then
    echo "[coverage] summary ${summary_line}"
  fi
fi
