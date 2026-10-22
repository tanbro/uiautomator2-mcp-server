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
TARGET="${OS}-${ARCH}"
if [[ "${OS}" == "unsupported" || "${ARCH}" == "unsupported" ]]; then
  echo "ERROR: unsupported platform ($(uname -s) $(uname -m))." >&2
  echo "Install from PyPI instead: uv tool install uiautomator2-mcp-server" >&2
  exit 1
fi

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
    DEFAULT_BASE="$(cygpath -u "${LOCALAPPDATA}" 2>/dev/null || printf '%s' "${LOCALAPPDATA}" | tr $'\\' '/')"
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

# --------------------------
# Resolve release asset via the channel manifest (latest.txt).
# Asset naming is owned by CI; this script only prefix-matches "u2mcp-<target>-".
# Plain HTTP download links are used so the GitHub API rate limit is irrelevant.
# --------------------------
VERSION="${U2MCP_VERSION:-latest}"
if [[ "${VERSION}" == "latest" ]]; then
  CHANNEL_URL="https://github.com/${GITHUB_REPO}/releases/latest/download/latest.txt"
  MANIFEST=$(http_get "${CHANNEL_URL}" || true)
  MANIFEST_SOURCE="the latest release"
else
  RELEASE_VERSION="${VERSION#v}"
  RELEASE_VERSION="${RELEASE_VERSION#V}"
  TAG="v${RELEASE_VERSION}"
  CHANNEL_URL="https://github.com/${GITHUB_REPO}/releases/download/${TAG}/latest.txt"
  MANIFEST=$(http_get "${CHANNEL_URL}" || true)
  MANIFEST_SOURCE="release ${TAG}"
fi

ASSET=$(printf '%s\n' "${MANIFEST}" | grep -m1 "^u2mcp-${TARGET}-" || true)
if [[ -z "${ASSET}" ]]; then
  echo "ERROR: no pre-built binary for ${TARGET} in ${MANIFEST_SOURCE}." >&2
  if [[ "${TARGET}" == "darwin-x64" ]]; then
    echo "Hint: Intel Macs have no pre-built binary. Install from PyPI: uv tool install uiautomator2-mcp-server" >&2
  fi
  echo "Hint: check supported platforms at ${CHANNEL_URL}" >&2
  exit 1
fi

# Derive the tag from the matched asset name; avoids relying on
# releases/latest/download redirects for the binary itself
TAG="v$(printf '%s' "${ASSET}" | sed -E "s/^u2mcp-${TARGET}-(.+)\.(tar\.gz|zip)$/\1/")"
DOWNLOAD_URL="https://github.com/${GITHUB_REPO}/releases/download/${TAG}/${ASSET}"

echo "=== u2mcp installer ==="
echo "Platform:  ${TARGET}"
echo "Version:   ${TAG}"
echo "Bundle:    ${BUNDLE_DIR}"
echo "Command:   ${BIN_LINK}"
echo "Archive:   ${DOWNLOAD_URL}"
echo

# --------------------------
# Download and extract
# --------------------------
TMP_DIR=$(mktemp -d -t u2mcp-install-XXXXXX)
trap 'rm -rf "${TMP_DIR}"' EXIT

echo "[1/3] Downloading ${ASSET}..."
http_get "${DOWNLOAD_URL}" > "${TMP_DIR}/${ASSET}"

echo "[2/3] Extracting..."
# Asset type decides the unpacker; CI ships zip on Windows, tar.gz elsewhere
if ! tar -xf "${TMP_DIR}/${ASSET}" -C "${TMP_DIR}" 2>/dev/null; then
  unzip -q -d "${TMP_DIR}" "${TMP_DIR}/${ASSET}"
fi

# --------------------------
# Replace bundle and link
# --------------------------
echo "[3/3] Installing to ${BUNDLE_DIR}..."
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
if ! "${BIN_LINK}" --version; then
  echo "ERROR: installed binary did not start. Try running it directly:" >&2
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
