#!/usr/bin/env bash
set -euo pipefail

DEST="${1:-artifacts/local}"
ROOT="$(pwd)"
mkdir -p "${DEST}"

is_excluded() {
  local rel="$1"
  case "${rel}" in
    tests/cases/*|docs/*|.github/*|tools/*|build/*|coverage/*|artifacts/*)
      return 0
      ;;
  esac
  return 1
}

moved=0
while IFS= read -r -d '' file; do
  rel="${file#${ROOT}/}"
  if is_excluded "${rel}"; then
    continue
  fi
  target="${DEST}/${rel}"
  mkdir -p "$(dirname "${target}")"
  mv "${file}" "${target}"
  moved=$((moved + 1))
done < <(
  find "${ROOT}" -type f \
    \( -name '*.exe' -o -name '*.o' -o -name '*.obj' -o -name '*.pdb' -o -name '*.ilk' -o -name '*.log' -o -name '*.txt' \) \
    -print0
)

echo "moved_artifacts=${moved}"

