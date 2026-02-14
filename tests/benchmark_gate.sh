#!/usr/bin/env bash
set -euo pipefail

JSONL="${1:-benchmark_results.jsonl}"
MIN_P50="${2:-2.0}"
MIN_P90="${3:-1.5}"
MODE="${4:-suite}"

if [[ ! -f "${JSONL}" ]]; then
  echo "Benchmark dosyasi bulunamadi: ${JSONL}"
  exit 1
fi

failed=0
p50_values=""
p90_values=""
while IFS= read -r line; do
  [[ -z "${line}" ]] && continue
  dosya="$(echo "${line}" | sed -n 's/.*"dosya":"\([^"]*\)".*/\1/p')"
  p50="$(echo "${line}" | sed -n 's/.*"p50_oran":\([-0-9.]*\).*/\1/p')"
  p90="$(echo "${line}" | sed -n 's/.*"p90_oran":\([-0-9.]*\).*/\1/p')"
  if [[ -z "${p50}" || -z "${p90}" ]]; then
    p50="$(echo "${line}" | sed -n 's/.*"p50_x":\([-0-9.]*\).*/\1/p')"
    p90="$(echo "${line}" | sed -n 's/.*"p90_x":\([-0-9.]*\).*/\1/p')"
  fi
  if [[ -z "${p50}" || -z "${p90}" ]]; then
    echo "[FAIL] ${dosya:-bilinmeyen} p50/p90 parse edilemedi."
    failed=1
    continue
  fi
  p50_values="${p50_values}${p50}"$'\n'
  p90_values="${p90_values}${p90}"$'\n'
  if [[ "${MODE}" == "per_case" ]]; then
    ok_p50="$(awk -v a="${p50}" -v b="${MIN_P50}" 'BEGIN{print (a>=b)?1:0}')"
    ok_p90="$(awk -v a="${p90}" -v b="${MIN_P90}" 'BEGIN{print (a>=b)?1:0}')"
    if [[ "${ok_p50}" -ne 1 || "${ok_p90}" -ne 1 ]]; then
      echo "[FAIL] ${dosya} P50=${p50} P90=${p90} (hedef ${MIN_P50}/${MIN_P90})"
      failed=1
    else
      echo "[OK] ${dosya} P50=${p50} P90=${p90}"
    fi
  else
    echo "[INFO] ${dosya} P50=${p50} P90=${p90}"
  fi
done < "${JSONL}"

if [[ "${MODE}" == "suite" ]]; then
  suite_p50="$(printf "%s" "${p50_values}" | awk 'NF{print $1}' | sort -n | awk '{a[NR]=$1} END{if(NR==0){print 0; exit} if(NR%2==1){print a[(NR+1)/2]} else {print (a[NR/2]+a[NR/2+1])/2}}')"
  suite_p90="$(printf "%s" "${p90_values}" | awk 'NF{print $1}' | sort -n | awk '{a[NR]=$1} END{if(NR==0){print 0; exit} if(NR%2==1){print a[(NR+1)/2]} else {print (a[NR/2]+a[NR/2+1])/2}}')"
  echo "[SUITE] median P50=${suite_p50} P90=${suite_p90} (hedef ${MIN_P50}/${MIN_P90})"
  ok_suite_p50="$(awk -v a="${suite_p50}" -v b="${MIN_P50}" 'BEGIN{print (a>=b)?1:0}')"
  ok_suite_p90="$(awk -v a="${suite_p90}" -v b="${MIN_P90}" 'BEGIN{print (a>=b)?1:0}')"
  if [[ "${ok_suite_p50}" -ne 1 || "${ok_suite_p90}" -ne 1 ]]; then
    failed=1
  fi
fi

if [[ "${failed}" -ne 0 ]]; then
  echo "Benchmark gate basarisiz."
  exit 1
fi

echo "Benchmark gate gecti."
