#!/usr/bin/env bash
set -euo pipefail

COMPILER="${1:-g++}"
OUTPUT="${2:-build/orhun_test}"

mkdir -p "$(dirname "${OUTPUT}")"

if [[ ! -f "${OUTPUT}" ]]; then
  echo "[vm-parity] Binary not found, building: ${OUTPUT}"
  "${COMPILER}" -std=c++17 -Wall -Wextra -pedantic \
    main.cpp Lexer.cpp Parser.cpp Interpreter.cpp Chunk.cpp Compiler.cpp VM.cpp \
    -o "${OUTPUT}"
fi

uname_lc="$(uname -s | tr '[:upper:]' '[:lower:]')"
mapfile -t cases < <(find tests/cases -maxdepth 1 -name '*.expected.txt' | sed 's#\\#/#g' | sed 's/\.expected\.txt$//' | sort)

filtered_cases=()
for case in "${cases[@]}"; do
  [[ -f "${case}.oh" ]] || continue
  if [[ "${uname_lc}" != *mingw* && "${uname_lc}" != *msys* && "${uname_lc}" != *cygwin* ]]; then
    case "${case}" in
      tests/cases/ffi_kernel32|tests/cases/ffi_text|tests/cases/ffi_symbol|tests/cases/ffi_tanimli_kernel32|tests/cases/ffi_dis_islev)
        continue
        ;;
    esac
  fi
  filtered_cases+=("${case}")
done

ok=0
fail=0
for case in "${filtered_cases[@]}"; do
  src="${case}.oh"
  expected_path="${case}.expected.txt"

  actual="$('./'"${OUTPUT}" vm-kati "${src}" 2>&1 || true)"
  expected="$(cat "${expected_path}")"

  actual="${actual%$'\n'}"
  expected="${expected%$'\n'}"

  if [[ "${actual}" != "${expected}" ]]; then
    echo "[VM-FAIL] ${src}"
    echo "Expected:"
    echo "${expected}"
    echo "Actual:"
    echo "${actual}"
    fail=$((fail + 1))
  else
    echo "[VM-OK] ${src}"
    ok=$((ok + 1))
  fi
done

echo "vm_parity_ok=${ok}"
echo "vm_parity_fail=${fail}"
if [[ "${fail}" -ne 0 ]]; then
  exit 1
fi
