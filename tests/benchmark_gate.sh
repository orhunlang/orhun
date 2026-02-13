#!/usr/bin/env bash
set -euo pipefail

JSONL="${1:-benchmark_results.jsonl}"
MIN_P50="${2:-2.0}"
MIN_P90="${3:-1.5}"

if [[ ! -f "${JSONL}" ]]; then
  echo "Benchmark dosyasi bulunamadi: ${JSONL}"
  exit 1
fi

failed=0
while IFS= read -r line; do
  [[ -z "${line}" ]] && continue
  dosya="$(echo "${line}" | sed -n 's/.*"dosya":"\([^"]*\)".*/\1/p')"
  p50="$(echo "${line}" | sed -n 's/.*"p50_x":\([-0-9.]*\).*/\1/p')"
  p90="$(echo "${line}" | sed -n 's/.*"p90_x":\([-0-9.]*\).*/\1/p')"
  if [[ -z "${p50}" || -z "${p90}" ]]; then
    echo "[FAIL] ${dosya:-bilinmeyen} p50/p90 parse edilemedi."
    failed=1
    continue
  fi
  ok_p50="$(awk -v a="${p50}" -v b="${MIN_P50}" 'BEGIN{print (a>=b)?1:0}')"
  ok_p90="$(awk -v a="${p90}" -v b="${MIN_P90}" 'BEGIN{print (a>=b)?1:0}')"
  if [[ "${ok_p50}" -ne 1 || "${ok_p90}" -ne 1 ]]; then
    echo "[FAIL] ${dosya} P50=${p50} P90=${p90} (hedef ${MIN_P50}/${MIN_P90})"
    failed=1
  else
    echo "[OK] ${dosya} P50=${p50} P90=${p90}"
  fi
done < "${JSONL}"

if [[ "${failed}" -ne 0 ]]; then
  echo "Benchmark gate basarisiz."
  exit 1
fi

echo "Benchmark gate gecti."
