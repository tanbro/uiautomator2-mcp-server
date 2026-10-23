#!/usr/bin/env bash
set -euo pipefail

APP_NAME="u2mcp"
GITHUB_REPO="tanbro/uiautomator2-mcp-server"
# --------------------------
# Platform detection
# --------------------------
get_os() {
  case "$(uname -s | tr '[:upper:]' '[:lower:]')" in
    linux*)            echo "linux" ;;
    darwin*)           echo "darwin" ;;
    *mingw*|*msys*|*cygwin*) echo "windows" ;;
    *)                 echo "unsupported" ;;
  esac
}

get_arch() {
  case "$(uname -m)" in
    x86_64|AMD64) echo "x64" ;;
    arm64|aarch64) echo "arm64" ;;
    *) echo "unsupported" ;;
  esac
}

OS=$(get_os)
ARCH=$(get_arch)
if [[ "${OS}" == "unsupported" || "${ARCH}" == "unsupported" ]]; then
  echo "ERROR: unsupported platform ($(uname -s) $(uname -m))." >&2
  echo "Install from PyPI instead: uv tool install uiautomator2-mcp-server" >&2
  exit 1
fi

# A Terminal forced to run under Rosetta 2 answers x86_64 to uname -m even on
# Apple Silicon, which would select the Intel target we never publish. The
# kernel knob is a contract (a named 0/1 value), so trust it over uname here.
if [[ "${OS}" == "darwin" && "${ARCH}" == "x64" ]]; then
  if [[ "$(sysctl -n sysctl.proc_translated 2>/dev/null || true)" == "1" ]]; then
    ARCH="arm64"
  fi
fi

# glibc-built bundles can never run on a musl system -- PyInstaller has no musl
# port, so there is no asset to select. Refuse before spending the download.
# The loader path is musl's own install contract, not a parsed command banner.
if [[ "${OS}" == "linux" ]]; then
  for musl_loader in /lib/ld-musl-*.so.1 /usr/lib/ld-musl-*.so.1; do
    if [[ -e "${musl_loader}" ]]; then
      echo "ERROR: this system uses musl libc (${musl_loader##*/}); pre-built u2mcp binaries are glibc-only." >&2
      echo "Install from PyPI instead: uv tool install uiautomator2-mcp-server" >&2
      exit 1
    fi
  done
fi

TARGET="${OS}-${ARCH}"

# --------------------------
# Install layout (user-level only).
# U2MCP_HOME overrides the bundle location.
# Unix:  bundle in the XDG data dir, command entry fixed at ~/.local/bin
#        (freedesktop convention; there is no XDG_BIN_HOME in any real spec).
# Windows (Git Bash/MSYS): bundle and command under %LOCALAPPDATA%\u2mcp.
# --------------------------
if [[ "${OS}" == "windows" ]]; then
  DEFAULT_BASE="${HOME}/AppData/Local"
  if [[ -n "${LOCALAPPDATA:-}" ]]; then
    # Without cygpath (plain MSYS), convert C:\x paths to slash form
    DEFAULT_BASE="$(cygpath -u "${LOCALAPPDATA}" 2>/dev/null || printf '%s' "${LOCALAPPDATA}" | tr '\\' '/')"
  fi
  BUNDLE_DIR="${U2MCP_HOME:-${DEFAULT_BASE}/${APP_NAME}}"
  BIN_DIR="${BUNDLE_DIR}/bin"
else
  BUNDLE_DIR="${U2MCP_HOME:-${XDG_DATA_HOME:-${HOME}/.local/share}/${APP_NAME}}"
  BIN_DIR="${HOME}/.local/bin"
fi
BIN_LINK="${BIN_DIR}/${APP_NAME}"

http_get() {
  if command -v curl &>/dev/null; then
    curl -fsSL "$1"
  elif command -v wget &>/dev/null; then
    wget -qO- "$1"
  else
    echo "ERROR: curl or wget is required." >&2
    exit 1
  fi
}

# macOS ships shasum but not sha256sum, so probe both.
sha256_of() {
  if command -v sha256sum &>/dev/null; then
    sha256sum "$1" | cut -d' ' -f1
  elif command -v shasum &>/dev/null; then
    shasum -a 256 "$1" | cut -d' ' -f1
  else
    echo "ERROR: sha256sum or shasum is required to verify the download." >&2
    exit 1
  fi
}

# --------------------------
# Resolve release asset via the channel manifest (SHA256SUMS), whose lines pair
# each asset name with its SHA256 digest. Asset naming is owned by CI; this
# script only prefix-matches "u2mcp-<target>-".
# Plain HTTP download links are used so the GitHub API rate limit is irrelevant.
# --------------------------
VERSION="${U2MCP_VERSION:-latest}"
if [[ "${VERSION}" == "latest" ]]; then
  CHANNEL_URL="https://github.com/${GITHUB_REPO}/releases/latest/download/SHA256SUMS"
  MANIFEST_SOURCE="the latest release"
else
  RELEASE_VERSION="${VERSION#v}"
  RELEASE_VERSION="${RELEASE_VERSION#V}"
  TAG="v${RELEASE_VERSION}"
  CHANNEL_URL="https://github.com/${GITHUB_REPO}/releases/download/${TAG}/SHA256SUMS"
  MANIFEST_SOURCE="release ${TAG}"
fi

# A failed fetch and a manifest without this platform are different problems:
# the first says the release or the network is unreachable, the second says no
# build exists for this target. Reporting them identically sends users hunting
# for a binary that was never published.
if ! MANIFEST=$(http_get "${CHANNEL_URL}" 2>/dev/null); then
  echo "ERROR: could not fetch the channel manifest${MANIFEST_SOURCE:+ from ${MANIFEST_SOURCE}}." >&2
  echo "  URL: ${CHANNEL_URL}" >&2
  echo "Either the network is unreachable or that release publishes no manifest." >&2
  exit 1
fi

CHANNEL_LINE=$(printf '%s\n' "${MANIFEST}" | grep -m1 -E "^[0-9a-f]{64}  u2mcp-${TARGET}-" || true)
if [[ -z "${CHANNEL_LINE}" ]]; then
  echo "ERROR: no pre-built binary for ${TARGET} in ${MANIFEST_SOURCE}." >&2
  if [[ "${TARGET}" == "darwin-x64" ]]; then
    echo "Hint: Intel Macs have no pre-built binary. Install from PyPI: uv tool install uiautomator2-mcp-server" >&2
  fi
  echo "Hint: check supported platforms at ${CHANNEL_URL}" >&2
  exit 1
fi
# The separator is exactly two spaces (CI writes sha256sum --text).
EXPECTED_SHA256=${CHANNEL_LINE%%  *}
ASSET=${CHANNEL_LINE#*  }

# The version is the last hyphen-delimited field of the asset name, so the
# naming stays CI-owned even if CI adds more fields (e.g. a libc token). An
# unexpected shape aborts rather than assembling a garbage download URL.
VERSION_FIELD=${ASSET##*-}
case "${VERSION_FIELD}" in
  *.tar.gz) VERSION_FIELD=${VERSION_FIELD%.tar.gz} ;;
  *.zip)    VERSION_FIELD=${VERSION_FIELD%.zip} ;;
esac
if [[ ! "${VERSION_FIELD}" =~ ^[0-9] ]]; then
  echo "ERROR: unexpected asset name in the manifest: ${ASSET}" >&2
  exit 1
fi
# Derived from the asset rather than the URL redirect, so the manifest and the
# binary it names cannot come from different releases.
TAG="v${VERSION_FIELD}"
DOWNLOAD_URL="https://github.com/${GITHUB_REPO}/releases/download/${TAG}/${ASSET}"

echo "=== u2mcp installer ==="
echo "Platform:  ${TARGET}"
echo "Version:   ${TAG}"
echo "Bundle:    ${BUNDLE_DIR}"
echo "Command:   ${BIN_LINK}"
echo "Archive:   ${DOWNLOAD_URL}"
echo "SHA256:    ${EXPECTED_SHA256}"
echo

# --------------------------
# Download, verify, extract
# --------------------------
TMP_DIR=$(mktemp -d -t u2mcp-install-XXXXXX)
trap 'rm -rf "${TMP_DIR}"' EXIT

echo "[1/5] Downloading ${ASSET}..."
http_get "${DOWNLOAD_URL}" > "${TMP_DIR}/${ASSET}"

# Checked before extraction so a corrupt or swapped archive fails while the
# previously installed bundle is still untouched.
echo "[2/5] Verifying SHA256..."
ACTUAL_SHA256=$(sha256_of "${TMP_DIR}/${ASSET}")
if [[ "${ACTUAL_SHA256}" != "${EXPECTED_SHA256}" ]]; then
  echo "ERROR: SHA256 mismatch for ${ASSET}. Nothing was installed." >&2
  echo "  expected: ${EXPECTED_SHA256}" >&2
  echo "  actual:   ${ACTUAL_SHA256}" >&2
  echo "The download is corrupt or the release changed after publishing." >&2
  exit 1
fi

echo "[3/5] Extracting..."
# Asset type decides the unpacker; CI ships zip on Windows, tar.gz elsewhere
if ! tar -xf "${TMP_DIR}/${ASSET}" -C "${TMP_DIR}" 2>/dev/null; then
  unzip -q -d "${TMP_DIR}" "${TMP_DIR}/${ASSET}"
fi

# The bundle's own exit code is the only contract-grade answer to "will this
# run here": a missing glibc loader and a glibc older than the build baseline
# both surface as a failed exec, without parsing any command's output. Run it
# on the extracted copy so a failure leaves the existing install intact.
echo "[4/5] Checking the bundle runs here..."
BUNDLE_EXE="${TMP_DIR}/${APP_NAME}/${APP_NAME}"
if [[ "${OS}" == "windows" ]]; then
  BUNDLE_EXE="${BUNDLE_EXE}.exe"
fi
chmod +x "${BUNDLE_EXE}"
if ! "${BUNDLE_EXE}" --version; then
  echo "ERROR: ${TAG} did not start on this system (${TARGET}); the existing install was left untouched." >&2
  echo "Hint: pre-built binaries need glibc at or above the baseline named in the asset name." >&2
  echo "Hint: install from PyPI instead: uv tool install uiautomator2-mcp-server" >&2
  exit 1
fi

# --------------------------
# Replace bundle and link
# --------------------------
echo "[5/5] Installing to ${BUNDLE_DIR}..."
rm -rf "${BUNDLE_DIR}"
mkdir -p "${BUNDLE_DIR}" "${BIN_DIR}"
# Archive root is u2mcp/: the binary plus its _internal runtime
cp -r "${TMP_DIR}/${APP_NAME}/"* "${BUNDLE_DIR}/"
rm -f "${BIN_LINK}"
if [[ "${OS}" == "windows" ]]; then
  # MSYS: a shell wrapper (not a symlink) around the .exe stays callable from bash
  chmod +x "${BUNDLE_DIR}/${APP_NAME}.exe"
  printf '#!/bin/sh\nexec "%s/%s.exe" "$@"\n' "${BUNDLE_DIR}" "${APP_NAME}" > "${BIN_LINK}"
  chmod +x "${BIN_LINK}"
else
  chmod +x "${BUNDLE_DIR}/${APP_NAME}"
  ln -s "${BUNDLE_DIR}/${APP_NAME}" "${BIN_LINK}"
fi

# --------------------------
# Verify
# --------------------------
# The bundle itself already ran from the temp dir, so this only proves the
# command entry just created here reaches it.
if ! "${BIN_LINK}" --version; then
  echo "ERROR: the ${APP_NAME} command did not start. Try running it directly:" >&2
  echo "  ${BIN_LINK} --version" >&2
  exit 1
fi
if ! command -v "${APP_NAME}" &>/dev/null; then
  echo "Note: add ${BIN_DIR} to your PATH to use the \"${APP_NAME}\" command:"
  echo "  export PATH=\"${BIN_DIR}:\$PATH\""
fi
if [[ "${OS}" == "darwin" ]]; then
  echo "Note: if Gatekeeper blocks the first run (unsigned build), clear quarantine:"
  echo "  xattr -d com.apple.quarantine \"${BUNDLE_DIR}/${APP_NAME}\""
fi

echo
echo "To uninstall:"
echo "  rm -rf ${BUNDLE_DIR} && rm -f ${BIN_LINK}"
