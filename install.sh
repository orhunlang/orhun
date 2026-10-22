#!/usr/bin/env bash
# Orhun one-line installer (Linux / macOS)
#
#   curl -fsSL https://raw.githubusercontent.com/orhunlang/orhun/v1.0.0/install.sh | bash
#
# Downloads the matching GitHub Release runtime archive, verifies SHA-256,
# installs under ~/.local/share/orhun, and links the binary into ~/.local/bin.

set -euo pipefail

REPO="${ORHUN_REPO:-orhunlang/orhun}"
VERSION="${ORHUN_VERSION:-1.0.0}"
PREFIX="${ORHUN_PREFIX:-${HOME}/.local/share/orhun}"
BIN_DIR="${ORHUN_BIN_DIR:-${HOME}/.local/bin}"
ARTIFACT="${ORHUN_ARTIFACT:-runtime}"

info() { printf '==> %s\n' "$*"; }
die() { printf 'error: %s\n' "$*" >&2; exit 1; }

detect_platform() {
  local os arch
  case "$(uname -s)" in
    Linux*) os=linux ;;
    Darwin*) os=macos ;;
    *) die "unsupported OS: $(uname -s)" ;;
  esac
  case "$(uname -m)" in
    x86_64 | amd64) arch=x64 ;;
    aarch64 | arm64) arch=arm64 ;;
    *) die "unsupported arch: $(uname -m)" ;;
  esac
  printf '%s-%s\n' "$os" "$arch"
}

command -v curl >/dev/null 2>&1 || die "curl is required"
command -v tar >/dev/null 2>&1 || die "tar is required"

PLATFORM="$(detect_platform)"
if [ "${PLATFORM#windows-}" != "${PLATFORM}" ]; then
  die "use install.ps1 on Windows"
fi

ARCHIVE="orhun-${ARTIFACT}-${VERSION}-${PLATFORM}.tar.gz"
BASE="https://github.com/${REPO}/releases/download/v${VERSION}"
TMP="$(mktemp -d)"
trap 'rm -rf "${TMP}"' EXIT

info "Downloading ${ARCHIVE}"
curl -fsSL "${BASE}/${ARCHIVE}" -o "${TMP}/${ARCHIVE}"
curl -fsSL "${BASE}/SHA256SUMS" -o "${TMP}/SHA256SUMS" || true

if [ -s "${TMP}/SHA256SUMS" ]; then
  info "Verifying SHA-256"
  expected="$(awk -v name="${ARCHIVE}" '$2 == name || $2 == ("*" name) {print $1}' "${TMP}/SHA256SUMS" | head -n1)"
  [ -n "${expected}" ] || die "SHA256SUMS entry not found for ${ARCHIVE}"
  actual="$( (sha256sum "${TMP}/${ARCHIVE}" 2>/dev/null || shasum -a 256 "${TMP}/${ARCHIVE}") | awk '{print $1}')"
  [ "${actual}" = "${expected}" ] || die "SHA-256 mismatch for ${ARCHIVE}"
else
  info "SHA256SUMS unavailable; skipping checksum verification"
fi

info "Extracting to ${PREFIX}"
mkdir -p "${PREFIX}"
tar -xzf "${TMP}/${ARCHIVE}" -C "${PREFIX}"

BIN_NAME=orhun
EXE="${PREFIX}/${BIN_NAME}"
if [ ! -x "${EXE}" ]; then
  # Archive may contain a single top-level directory.
  candidate="$(find "${PREFIX}" -maxdepth 2 -type f -name orhun | head -n1 || true)"
  [ -n "${candidate}" ] || die "orhun binary not found in archive"
  EXE="${candidate}"
  chmod +x "${EXE}"
fi

mkdir -p "${BIN_DIR}"
ln -sfn "${EXE}" "${BIN_DIR}/orhun"
info "Installed: ${BIN_DIR}/orhun -> ${EXE}"

case ":${PATH}:" in
  *":${BIN_DIR}:"*) ;;
  *)
    info "Add ${BIN_DIR} to PATH, for example:"
    printf '  export PATH="%s:$PATH"\n' "${BIN_DIR}"
    ;;
esac

"${BIN_DIR}/orhun" surum || true
info "Done. Run: orhun yardim"
