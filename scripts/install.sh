#!/usr/bin/env bash
set -euo pipefail

APP_NAME="u2mcp"
GITHUB_REPO="tanbro/uiautomator2‑mcp"
# bundle 本体固定路径
APP_LIB="${HOME}/.local/lib/${APP_NAME}"

# --------------------------
# 探测 BIN_DIR：放 symlink 的目录
# 优先级：U2MCP_INSTALL_BIN > XDG_BIN_DIR > ~/bin > ~/.u2mcp/bin
# --------------------------
if [[ -n "${U2MCP_INSTALL_BIN:-}" ]]; then
  BIN_DIR="${U2MCP_INSTALL_BIN}"
elif [[ -n "${XDG_BIN_DIR:-}" ]]; then
  BIN_DIR="${XDG_BIN_DIR}"
elif [[ -d "${HOME}/bin" ]]; then
  BIN_DIR="${HOME}/bin"
else
  BIN_DIR="${HOME}/.${APP_NAME}/bin"
fi
BIN_LINK="${BIN_DIR}/${APP_NAME}"

# --------------------------
# 平台识别
# --------------------------
get_arch() {
  local arch
  arch=$(uname -m)
  case "${arch}" in
    x86_64) echo "x64" ;;
    arm64|aarch64) echo "arm64" ;;
    *) echo "unsupported" ;;
  esac
}

get_os() {
  local os
  os=$(uname -s | tr '[:upper:]' '[:lower:]')
  case "${os}" in
    linux) echo "linux" ;;
    darwin) echo "darwin" ;;
    *) echo "unsupported" ;;
  esac
}

OS=$(get_os)
ARCH=$(get_arch)
if [[ "${OS}" == "unsupported" || "${ARCH}" == "unsupported" ]]; then
  echo "ERROR: unsupported OS/arch: $(uname -s) $(uname -m)" >&2
  exit 1
fi

# --------------------------
# 解析版本，默认 latest
# --------------------------
VERSION="${U2MCP_VERSION:-latest}"
if [[ "${VERSION}" == "latest" ]]; then
  DOWNLOAD_URL="https://github.com/${GITHUB_REPO}/releases/latest/download/${APP_NAME}-${OS}-${ARCH}.zip"
else
  DOWNLOAD_URL="https://github.com/${GITHUB_REPO}/releases/download/${VERSION}/${APP_NAME}-${OS}-${ARCH}.zip"
fi

echo "=== u2mcp installer ==="
echo "OS:         ${OS}"
echo "Arch:       ${ARCH}"
echo "Bundle dir: ${APP_LIB}"
echo "Entry dir:  ${BIN_DIR}"
echo "Download:   ${DOWNLOAD_URL}"
echo

# --------------------------
# 准备临时目录
# --------------------------
TMP_DIR=$(mktemp -d -t u2mcp-install-XXXXXX)
trap 'rm -rf "${TMP_DIR}"' EXIT
ZIP_FILE="${TMP_DIR}/${APP_NAME}.zip"

# --------------------------
# 下载
# --------------------------
echo "Downloading archive..."
if command -v curl &>/dev/null; then
  curl -fsSL --output "${ZIP_FILE}" "${DOWNLOAD_URL}"
elif command -v wget &>/dev/null; then
  wget -q -O "${ZIP_FILE}" "${DOWNLOAD_URL}"
else
  echo "ERROR: curl or wget required" >&2
  exit 1
fi

# --------------------------
# 解压
# --------------------------
echo "Extracting archive..."
unzip -q -d "${TMP_DIR}" "${ZIP_FILE}"

# --------------------------
# 替换 bundle 本体
# --------------------------
echo "Installing runtime bundle to ${APP_LIB}"
rm -rf "${APP_LIB}"
mkdir -p "${APP_LIB}"
# zip根目录是 u2mcp/，内部包含二进制 + _internal
cp -r "${TMP_DIR}/${APP_NAME}/"* "${APP_LIB}/"
chmod +x "${APP_LIB}/${APP_NAME}"

# --------------------------
# 创建 symlink
# --------------------------
mkdir -p "${BIN_DIR}"
rm -f "${BIN_LINK}"
ln -s "${APP_LIB}/${APP_NAME}" "${BIN_LINK}"

# --------------------------
# 校验
# --------------------------
echo
if command -v "${APP_NAME}" &>/dev/null; then
  echo "✅ Install succeeded. Version output:"
  "${APP_NAME}" --version
else
  echo "✅ Files installed, but command \"${APP_NAME}\" is not found in current PATH."
  echo "Hint: add \"${BIN_DIR}\" to your shell PATH."
  echo "For bash/zsh: export PATH=\"${BIN_DIR}:\$PATH\""
fi

echo
echo "Uninstall commands:"
echo "  rm -rf ${APP_LIB}"
echo "  rm -f ${BIN_LINK}"
echo "  # rm -rf ~/.config/${APP_NAME}  # optional purge user config"
