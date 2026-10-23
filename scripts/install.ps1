<#
.SYNOPSIS
u2mcp standalone (one-dir) installer. Works on Windows PowerShell 5.1+
and PowerShell 7+ on Linux/macOS.
#>
$ErrorActionPreference = "Stop"

$APP_NAME = "u2mcp"
$GITHUB_REPO = "tanbro/uiautomator2-mcp-server"

# --------------------------
# Platform detection from runtime facts (pwsh runs on Windows and Unix)
# --------------------------
try {
    $rt = [System.Runtime.InteropServices.RuntimeInformation]
    if ($rt::IsOSPlatform([System.Runtime.InteropServices.OSPlatform]::Windows)) { $OS = "windows" }
    elseif ($rt::IsOSPlatform([System.Runtime.InteropServices.OSPlatform]::OSX))  { $OS = "darwin" }
    else                                                                           { $OS = "linux" }
} catch {
    # PS 5.1 on .NET Framework < 4.7.1 lacks IsOSPlatform; there it is always Windows
    $OS = if ($env:OS -eq "Windows_NT") { "windows" } else { "linux" }
}

# OSArchitecture reports the real native arch (e.g. ARM64 under x64 emulation),
# unlike Is64BitOperatingSystem. Windows on ARM runs x64 binaries via
# emulation, so arm64 maps to x64 on Windows only.
$arch = try {
    $a = $rt::OSArchitecture.ToString()
    $a = $a.Substring(0, 1).ToLower() + $a.Substring(1)
    switch ($a) {
        "arm64" { if ($OS -eq "windows") { "x64" } else { "arm64" } }
        default { $a }
    }
} catch {
    if ([Environment]::Is64BitOperatingSystem) { "x64" } else { "x86" }
}
$IS_WINDOWS = ($OS -eq "windows")
$TARGET = "$OS-$arch"
$PREFIX = "u2mcp-$TARGET-"

# --------------------------
# Install layout (user-level only).
# U2MCP_HOME overrides the bundle location. On Windows the command wrapper
# lives next to the bundle; on Unix it goes to ~/.local/bin.
# --------------------------
if ($IS_WINDOWS) {
    $LOCAL_APPDATA = if ($env:LOCALAPPDATA) { $env:LOCALAPPDATA } else { Join-Path $HOME "AppData\Local" }
    $DEFAULT_BUNDLE = Join-Path $LOCAL_APPDATA $APP_NAME
    $BIN_DIR = Join-Path $DEFAULT_BUNDLE "bin"
    $COMMAND_PATH = Join-Path $BIN_DIR "$APP_NAME.cmd"
    if (${env:U2MCP_HOME}) {
        $BUNDLE_DIR = ${env:U2MCP_HOME}
        $BIN_DIR = Join-Path $BUNDLE_DIR "bin"
        $COMMAND_PATH = Join-Path $BIN_DIR "$APP_NAME.cmd"
    }
    else {
        $BUNDLE_DIR = $DEFAULT_BUNDLE
    }
}
else {
    $XDG_DATA = if ($env:XDG_DATA_HOME) { $env:XDG_DATA_HOME } else { Join-Path $HOME ".local/share" }
    $BUNDLE_DIR = if (${env:U2MCP_HOME}) { ${env:U2MCP_HOME} } else { Join-Path $XDG_DATA $APP_NAME }
    $BIN_DIR = Join-Path $HOME ".local/bin"
    $COMMAND_PATH = Join-Path $BIN_DIR $APP_NAME
}

# --------------------------
# Resolve release asset via the channel manifest (sha256sums.txt), whose lines
# pair each asset name with its SHA256 digest. Asset naming is owned by CI;
# this script only prefix-matches "u2mcp-<target>-".
# Plain HTTP download links are used so the GitHub API rate limit is irrelevant.
# --------------------------
$VERSION = if ($env:U2MCP_VERSION) { $env:U2MCP_VERSION } else { "latest" }
if ($VERSION -eq "latest") {
    $CHANNEL_URL = "https://github.com/$GITHUB_REPO/releases/latest/download/sha256sums.txt"
    $MANIFEST_SOURCE = "the latest release"
}
else {
    $RELEASE_VERSION = $VERSION.TrimStart('v','V')
    $TAG = "v$RELEASE_VERSION"
    $CHANNEL_URL = "https://github.com/$GITHUB_REPO/releases/download/$TAG/sha256sums.txt"
    $MANIFEST_SOURCE = "release $TAG"
}
try {
    $MANIFEST = ((Invoke-WebRequest -Uri $CHANNEL_URL -UseBasicParsing).Content) -split "`r?`n"
} catch {
    Write-Host "ERROR: failed to fetch the channel manifest."
    Write-Host "  URL: $CHANNEL_URL"
    exit 1
}
$CHANNEL_LINE = $MANIFEST | Where-Object { $_ -match ("^[0-9a-f]{64}  " + [regex]::Escape($PREFIX)) } | Select-Object -First 1
if (-not $CHANNEL_LINE) {
    Write-Host "ERROR: no pre-built binary for $TARGET in $MANIFEST_SOURCE."
    Write-Host "  Hint: check supported platforms at $CHANNEL_URL"
    exit 1
}
$MANIFEST_FIELDS = $CHANNEL_LINE -split '\s+', 2
$EXPECTED_SHA256 = $MANIFEST_FIELDS[0]
$ASSET = $MANIFEST_FIELDS[1]

# Derive the tag from the matched asset name
$TAG = "v" + ($ASSET -replace ("^" + [regex]::Escape($PREFIX) + "(.+)\.(zip|tar\.gz)$"), '$1')
$DOWNLOAD_URL = "https://github.com/$GITHUB_REPO/releases/download/$TAG/$ASSET"

Write-Host "=== u2mcp installer ==="
Write-Host "Platform:  $TARGET"
Write-Host "Version:   $TAG"
Write-Host "Bundle:    $BUNDLE_DIR"
Write-Host "Command:   $COMMAND_PATH"
Write-Host "Archive:   $DOWNLOAD_URL"
Write-Host "SHA256:    $EXPECTED_SHA256"
Write-Host ""

# --------------------------
# Download, verify, extract, install
# --------------------------
$TMP_DIR = Join-Path ([IO.Path]::GetTempPath()) ("u2mcp-install-" + [Guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $TMP_DIR | Out-Null
try {
    $ARCHIVE = Join-Path $TMP_DIR $ASSET

    Write-Host "[1/4] Downloading $ASSET..."
    Invoke-WebRequest -Uri $DOWNLOAD_URL -OutFile $ARCHIVE -UseBasicParsing

    # Checked before extraction so a corrupt or swapped archive fails while the
    # previously installed bundle is still untouched.
    Write-Host "[2/4] Verifying SHA256..."
    $ACTUAL_SHA256 = (Get-FileHash -Algorithm SHA256 $ARCHIVE).Hash.ToLower()
    if ($ACTUAL_SHA256 -ne $EXPECTED_SHA256) {
        Write-Host "ERROR: SHA256 mismatch for $ASSET. Nothing was installed."
        Write-Host "  expected: $EXPECTED_SHA256"
        Write-Host "  actual:   $ACTUAL_SHA256"
        Write-Host "The download is corrupt or the release changed after publishing."
        exit 1
    }

    Write-Host "[3/4] Extracting..."
    if ($ASSET -like "*.zip") {
        Expand-Archive -Path $ARCHIVE -DestinationPath $TMP_DIR -Force
    }
    else {
        & tar -xzf $ARCHIVE -C $TMP_DIR
        if ($LASTEXITCODE -ne 0) { throw "tar failed with exit code $LASTEXITCODE" }
    }

    Write-Host "[4/4] Installing to $BUNDLE_DIR..."
    if (Test-Path $BUNDLE_DIR) {
        Remove-Item -Path $BUNDLE_DIR -Recurse -Force
    }
    New-Item -ItemType Directory -Path $BUNDLE_DIR -Force | Out-Null
    # Archive root is u2mcp/: the binary plus its _internal runtime
    Copy-Item -Path (Join-Path $TMP_DIR "$APP_NAME/*") -Destination $BUNDLE_DIR -Recurse -Force

    $bundleExe = Join-Path $BUNDLE_DIR $APP_NAME
    if ($IS_WINDOWS) {
        $bundleExe += ".exe"
        "@echo off`n`"$bundleExe`" %*" | Out-File -FilePath $COMMAND_PATH -Encoding ASCII
    }
    else {
        chmod +x "$bundleExe"
        if ($LASTEXITCODE -ne 0) { throw "chmod failed with exit code $LASTEXITCODE" }
        "#!/bin/sh`nexec `"$bundleExe`" `"`$@" | Out-File -FilePath $COMMAND_PATH -Encoding ascii
        chmod +x "$COMMAND_PATH"
        if ($LASTEXITCODE -ne 0) { throw "chmod failed with exit code $LASTEXITCODE" }
    }
}
finally {
    Remove-Item -Path $TMP_DIR -Recurse -Force -ErrorAction SilentlyContinue
}

# --------------------------
# Verify
# --------------------------
try {
    & $COMMAND_PATH --version
} catch {
    Write-Host "ERROR: installed command did not run. Try directly:"
    Write-Host "  $COMMAND_PATH --version"
    exit 1
}
if ($null -eq (Get-Command $APP_NAME -ErrorAction SilentlyContinue)) {
    Write-Host "Note: add $BIN_DIR to your PATH to use the `"$APP_NAME`" command."
}

Write-Host ""
Write-Host "To uninstall:"
Write-Host "  Remove-Item -Path `"$BUNDLE_DIR`" -Recurse -Force; Remove-Item -Path `"$COMMAND_PATH`" -Force"
