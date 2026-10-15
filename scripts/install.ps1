<#
.SYNOPSIS
u2mcp one‑dir installer for Windows
#>
$ErrorActionPreference = "Stop"

$APP_NAME = "u2mcp"
$GITHUB_REPO = "tanbro/uiautomator2‑mcp"
# bundle本体固定路径
$APP_LIB = Join-Path $HOME ".local\lib\$APP_NAME"

# --------------------------
# 探测 BIN_DIR
# 优先级：U2MCP_INSTALL_BIN > XDG_BIN_DIR > $HOME\bin > $HOME\.u2mcp\bin
# --------------------------
if ($env:U2MCP_INSTALL_BIN) {
    $BIN_DIR = $env:U2MCP_INSTALL_BIN
}
elseif ($env:XDG_BIN_DIR) {
    $BIN_DIR = $env:XDG_BIN_DIR
}
elseif (Test-Path (Join-Path $HOME "bin")) {
    $BIN_DIR = Join-Path $HOME "bin"
}
else {
    $BIN_DIR = Join-Path $HOME ".u2mcp\bin"
}
$WRAPPER_PATH = Join-Path $BIN_DIR "$APP_NAME.cmd"

# --------------------------
# 平台
# --------------------------
$OS = "windows"
$arch = [Environment]::Is64BitOperatingSystem ? "x64" : "x86"

# --------------------------
# 版本
# --------------------------
$VERSION = if ($env:U2MCP_VERSION) { $env:U2MCP_VERSION } else { "latest" }
if ($VERSION -eq "latest") {
    $DOWNLOAD_URL = "https://github.com/$GITHUB_REPO/releases/latest/download/$APP_NAME-$OS-$arch.zip"
}
else {
    $DOWNLOAD_URL = "https://github.com/$GITHUB_REPO/releases/download/$VERSION/$APP_NAME-$OS-$arch.zip"
}

Write-Host "=== u2mcp installer ==="
Write-Host "OS:         $OS"
Write-Host "Arch:       $arch"
Write-Host "Bundle dir: $APP_LIB"
Write-Host "Entry dir:  $BIN_DIR"
Write-Host "Download:   $DOWNLOAD_URL"
Write-Host ""

# 临时目录
$TMP_DIR = Join-Path $env:TEMP ("u2mcp-install-" + [Guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $TMP_DIR | Out-Null
try {
    $ZIP_FILE = Join-Path $TMP_DIR "$APP_NAME.zip"

    Write-Host "Downloading archive..."
    Invoke-WebRequest -Uri $DOWNLOAD_URL -OutFile $ZIP_FILE -UseBasicParsing

    Write-Host "Extracting archive..."
    Expand-Archive -Path $ZIP_FILE -DestinationPath $TMP_DIR -Force

    Write-Host "Installing runtime bundle to $APP_LIB"
    if (Test-Path $APP_LIB) {
        Remove-Item -Path $APP_LIB -Recurse -Force
    }
    New-Item -ItemType Directory -Path $APP_LIB -Force | Out-Null
    $src = Join-Path $TMP_DIR "$APP_NAME\*"
    Copy-Item -Path $src -Destination $APP_LIB -Recurse -Force

    # 生成 thin cmd wrapper
    New-Item -ItemType Directory -Path $BIN_DIR -Force | Out-Null
    $exePath = Join-Path $APP_LIB "$APP_NAME.exe"
    "@echo off`n`"$exePath`" %*" | Out-File -FilePath $WRAPPER_PATH -Encoding ASCII

    Write-Host ""
    # 简单校验
    $cmdExists = $null -ne (Get-Command $APP_NAME -ErrorAction SilentlyContinue)
    if ($cmdExists) {
        Write-Host "✅ Install succeeded."
        & $APP_NAME --version
    }
    else {
        Write-Host "✅ Files installed, but command `"$APP_NAME`" not found in current PATH."
        Write-Host "Hint: add `"$BIN_DIR`" to user PATH environment variable, restart terminal."
    }

    Write-Host ""
    Write-Host "Uninstall PowerShell commands:"
    Write-Host "Remove-Item -Path `"$APP_LIB`" -Recurse -Force"
    Write-Host "Remove-Item -Path `"$WRAPPER_PATH`" -Force -ErrorAction SilentlyContinue"
    Write-Host "# Remove-Item -Path `$env:APPDATA\$APP_NAME -Recurse -Force  # optional purge user config"
}
finally {
    Remove-Item -Path $TMP_DIR -Recurse -Force -ErrorAction SilentlyContinue
}
