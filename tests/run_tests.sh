#!/usr/bin/env bash
set -euo pipefail

COMPILER="${1:-g++}"
OUTPUT="${2:-build/orhun_test}"
TEST_TIMEOUT_SECONDS="${ORHUN_TEST_TIMEOUT_SECONDS:-10}"
SKIP_BUILD="${ORHUN_SKIP_BUILD:-0}"
REPO_ROOT="$(pwd -P)"
case "${OUTPUT}" in
  /*) ABS_OUTPUT="${OUTPUT}" ;;
  *) ABS_OUTPUT="${REPO_ROOT}/${OUTPUT}" ;;
esac

path_for_orhun() {
  if command -v cygpath >/dev/null 2>&1; then
    cygpath -w "$1"
  else
    printf '%s' "$1"
  fi
}

if command -v cygpath >/dev/null 2>&1; then
  STD_LIB_PATH="$(path_for_orhun "${REPO_ROOT}/StdLib");$(path_for_orhun "${REPO_ROOT}")"
else
  STD_LIB_PATH="${REPO_ROOT}/StdLib:${REPO_ROOT}"
fi
WORK_ROOT="${REPO_ROOT}/build/test-work/run-tests-$$"

mkdir -p "$(dirname "${OUTPUT}")"
mkdir -p "${WORK_ROOT}"

if [[ "${SKIP_BUILD}" == "1" ]]; then
  echo "[1/3] Using existing binary..."
  if [[ ! -f "${OUTPUT}" ]]; then
    echo "Existing test binary not found: ${OUTPUT}" >&2
    exit 2
  fi
else
  echo "[1/3] Building..."
  "${COMPILER}" -std=c++17 -Wall -Wextra -pedantic \
    main.cpp Lexer.cpp Parser.cpp Interpreter.cpp Chunk.cpp Compiler.cpp VM.cpp \
    -o "${OUTPUT}"
fi

uname_lc="$(uname -s | tr '[:upper:]' '[:lower:]')"
cases=()
while IFS= read -r test_case; do
  cases+=("${test_case}")
done < <(find tests/cases -maxdepth 1 -name '*.expected.txt' | sed 's#\\#/#g' | sed 's/\.expected\.txt$//' | sort)

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
cases=("${filtered_cases[@]}")
strict_turkce_case="tests/cases/turkce_kati_alias"

run_orhun() {
  local src="$1"
  local workdir="$2"
  local actual=""
  local status=0
  if command -v timeout >/dev/null 2>&1; then
    set +e
    actual="$(cd "${workdir}" && ORHUN_STDLIB_PATH="${STD_LIB_PATH}" timeout "${TEST_TIMEOUT_SECONDS}s" "${ABS_OUTPUT}" "${src}" 2>&1)"
    status=$?
    set -e
    if [[ "${status}" -eq 124 || "${status}" -eq 137 ]]; then
      printf 'Hata: test zaman asimi (%ss)' "${TEST_TIMEOUT_SECONDS}"
      return 0
    fi
  else
    set +e
    actual="$(cd "${workdir}" && ORHUN_STDLIB_PATH="${STD_LIB_PATH}" "${ABS_OUTPUT}" "${src}" 2>&1)"
    status=$?
    set -e
  fi

  printf '%s' "${actual}"
  if [[ "${status}" -ne 0 && "${status}" -ne 1 ]]; then
    if [[ -n "${actual}" ]]; then
      printf '\n'
    fi
    printf 'Hata: beklenmeyen cikis kodu (%s)' "${status}"
  fi
}

failed=0
echo "[2/3] Running tests..."
for case in "${cases[@]}"; do
  if [[ "${case}" == "${strict_turkce_case}" ]]; then
    continue
  fi
  src="${case}.oh"
  expected_path="${case}.expected.txt"
  abs_src="$(path_for_orhun "${REPO_ROOT}/${src}")"
  case_workdir="${WORK_ROOT}/$(basename "${case}")"
  mkdir -p "${case_workdir}"

  actual="$(run_orhun "${abs_src}" "${case_workdir}")"
  expected="$(cat "${expected_path}")"

  actual="${actual//$'\r\n'/$'\n'}"
  actual="${actual//$'\r'/}"
  expected="${expected//$'\r\n'/$'\n'}"
  expected="${expected//$'\r'/}"

  # normalize trailing newline differences
  actual="${actual%$'\n'}"
  expected="${expected%$'\n'}"

  if [[ "${actual}" != "${expected}" ]]; then
    echo ""
    echo "[FAIL] ${src}"
    echo "Expected:"
    echo "${expected}"
    echo "Actual:"
    echo "${actual}"
    failed=1
  else
    echo "[OK] ${src}"
  fi
done

if [[ -f "${strict_turkce_case}.oh" && -f "${strict_turkce_case}.expected.txt" ]]; then
  src="${strict_turkce_case}.oh"
  expected_path="${strict_turkce_case}.expected.txt"
  abs_src="$(path_for_orhun "${REPO_ROOT}/${src}")"
  case_workdir="${WORK_ROOT}/$(basename "${strict_turkce_case}")"
  mkdir -p "${case_workdir}"
  actual="$(ORHUN_TURKCE_KATI=1 run_orhun "${abs_src}" "${case_workdir}")"
  expected="$(cat "${expected_path}")"
  actual="${actual//$'\r\n'/$'\n'}"
  actual="${actual//$'\r'/}"
  expected="${expected//$'\r\n'/$'\n'}"
  expected="${expected//$'\r'/}"
  actual="${actual%$'\n'}"
  expected="${expected%$'\n'}"
  if [[ "${actual}" != "${expected}" ]]; then
    echo ""
    echo "[FAIL] ${src} (ORHUN_TURKCE_KATI=1)"
    echo "Expected:"
    echo "${expected}"
    echo "Actual:"
    echo "${actual}"
    failed=1
  else
    echo "[OK] ${src} (ORHUN_TURKCE_KATI=1)"
  fi
fi

echo "[3/3] Result..."
if [[ "${failed}" -ne 0 ]]; then
  echo "Some tests failed."
  exit 1
fi
echo "All tests passed."
