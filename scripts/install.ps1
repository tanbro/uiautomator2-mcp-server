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

# A Terminal forced under Rosetta 2 makes an x64 pwsh believe it is on an Intel
# Mac, which would select a target we never publish. The kernel knob is a
# contract (a named 0/1 value), so prefer it over the reported architecture.
if ($OS -eq "darwin" -and $arch -eq "x64") {
    $translated = try { (& sysctl -n sysctl.proc_translated 2>$null | Out-String).Trim() } catch { "" }
    if ($translated -eq "1") { $arch = "arm64" }
}

# glibc-built bundles can never run on a musl system -- PyInstaller has no musl
# port, so there is no asset to select. Refuse before spending the download.
# The loader path is musl's own install contract, not a parsed command banner.
if ($OS -eq "linux" -and (Get-ChildItem -Path "/lib", "/usr/lib" -Filter "ld-musl-*.so.1" -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: this system uses musl libc; pre-built u2mcp binaries are glibc-only."
    Write-Host "Install from PyPI instead: uv tool install uiautomator2-mcp-server"
    exit 1
}

# Map the detected pair onto a release target triple. CI mints the triples (see
# .github/workflows/ci.yml); this table is the only naming knowledge the script
# carries, and an unmapped pair means "we do not build for you" -- known here,
# before spending a manifest fetch on a guess. Windows on ARM already collapsed
# to x64 above, so it needs no row.
$TRIPLE = switch ("$OS/$arch") {
    "linux/x64"    { "x86_64-unknown-linux-gnu" }
    "linux/arm64"  { "aarch64-unknown-linux-gnu" }
    "darwin/arm64" { "aarch64-apple-darwin" }
    "windows/x64"  { "x86_64-pc-windows-msvc" }
    default        { $null }
}
if (-not $TRIPLE) {
    Write-Host "ERROR: no pre-built binary for $OS-$arch."
    if ($OS -eq "darwin" -and $arch -eq "x64") {
        Write-Host "Hint: Intel Macs have no pre-built binary. Install from PyPI: uv tool install uiautomator2-mcp-server"
    }
    else {
        Write-Host "Install from PyPI instead: uv tool install uiautomator2-mcp-server"
    }
    exit 1
}
$PREFIX = "u2mcp-$TRIPLE-"

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
# Resolve release asset via the channel manifest (SHA256SUMS), whose lines pair
# each asset name with its SHA256 digest. Asset naming is owned by CI;
# this script only maps uname onto a target triple and prefix-matches "u2mcp-<triple>-".
# Plain HTTP download links are used so the GitHub API rate limit is irrelevant.
# --------------------------
$VERSION = if ($env:U2MCP_VERSION) { $env:U2MCP_VERSION } else { "latest" }
if ($VERSION -eq "latest") {
    $CHANNEL_URL = "https://github.com/$GITHUB_REPO/releases/latest/download/SHA256SUMS"
    $MANIFEST_SOURCE = "the latest release"
}
else {
    $RELEASE_VERSION = $VERSION.TrimStart('v','V')
    $TAG = "v$RELEASE_VERSION"
    $CHANNEL_URL = "https://github.com/$GITHUB_REPO/releases/download/$TAG/SHA256SUMS"
    $MANIFEST_SOURCE = "release $TAG"
}
# A failed fetch and a manifest without this platform are different problems:
# reporting them identically sends users hunting for a binary that was never
# published.
try {
    $MANIFEST = ((Invoke-WebRequest -Uri $CHANNEL_URL -UseBasicParsing).Content) -split "`r?`n"
} catch {
    Write-Host "ERROR: could not fetch the channel manifest from $MANIFEST_SOURCE."
    Write-Host "  URL: $CHANNEL_URL"
    Write-Host "Either the network is unreachable or that release publishes no manifest."
    exit 1
}
$CHANNEL_LINE = $MANIFEST | Where-Object { $_ -match ("^[0-9a-f]{64}  " + [regex]::Escape($PREFIX)) } | Select-Object -First 1
if (-not $CHANNEL_LINE) {
    Write-Host "ERROR: no pre-built binary for $TRIPLE in $MANIFEST_SOURCE."
    Write-Host "  Hint: check supported platforms at $CHANNEL_URL"
    exit 1
}
$MANIFEST_FIELDS = $CHANNEL_LINE -split '\s+', 2
$EXPECTED_SHA256 = $MANIFEST_FIELDS[0]
$ASSET = $MANIFEST_FIELDS[1]

# The version is the last hyphen-delimited field of the asset name, so the
# naming stays CI-owned even if CI adds more fields (e.g. a libc token). An
# unexpected shape aborts rather than assembling a garbage download URL.
$VERSION_FIELD = (($ASSET -split '-')[-1] -replace '\.(tar\.gz|zip)$', '')
if ($VERSION_FIELD -notmatch '^[0-9]') {
    Write-Host "ERROR: unexpected asset name in the manifest: $ASSET"
    exit 1
}
# Derived from the asset rather than the URL redirect, so the manifest and the
# binary it names cannot come from different releases.
$TAG = "v$VERSION_FIELD"
$DOWNLOAD_URL = "https://github.com/$GITHUB_REPO/releases/download/$TAG/$ASSET"

Write-Host "=== u2mcp installer ==="
Write-Host "Target:    $TRIPLE"
Write-Host "Version:   $TAG"
Write-Host "Bundle:    $BUNDLE_DIR"
Write-Host "Command:   $COMMAND_PATH"
Write-Host "Archive:   $DOWNLOAD_URL"
Write-Host "SHA256:    $EXPECTED_SHA256"
Write-Host ""

# --------------------------
# Download, verify, extract, smoke-test, install
# --------------------------
$TMP_DIR = Join-Path ([IO.Path]::GetTempPath()) ("u2mcp-install-" + [Guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $TMP_DIR | Out-Null
try {
    $ARCHIVE = Join-Path $TMP_DIR $ASSET

    Write-Host "[1/5] Downloading $ASSET..."
    Invoke-WebRequest -Uri $DOWNLOAD_URL -OutFile $ARCHIVE -UseBasicParsing

    # Checked before extraction so a corrupt or swapped archive fails while the
    # previously installed bundle is still untouched.
    Write-Host "[2/5] Verifying SHA256..."
    $ACTUAL_SHA256 = (Get-FileHash -Algorithm SHA256 $ARCHIVE).Hash.ToLower()
    if ($ACTUAL_SHA256 -ne $EXPECTED_SHA256) {
        Write-Host "ERROR: SHA256 mismatch for $ASSET. Nothing was installed."
        Write-Host "  expected: $EXPECTED_SHA256"
        Write-Host "  actual:   $ACTUAL_SHA256"
        Write-Host "The download is corrupt or the release changed after publishing."
        exit 1
    }

    Write-Host "[3/5] Extracting..."
    if ($ASSET -like "*.zip") {
        Expand-Archive -Path $ARCHIVE -DestinationPath $TMP_DIR -Force
    }
    else {
        & tar -xzf $ARCHIVE -C $TMP_DIR
        if ($LASTEXITCODE -ne 0) { throw "tar failed with exit code $LASTEXITCODE" }
    }

    Write-Host "[4/5] Checking the bundle runs here..."
    # The archive root is u2mcp/, so the extracted exe sits one level deeper
    # than the flat BUNDLE_DIR layout used after the copy.
    $tempExe = Join-Path (Join-Path $TMP_DIR $APP_NAME) $APP_NAME
    if ($IS_WINDOWS) {
        $tempExe += ".exe"
    }
    if (-not (Test-Path $tempExe)) {
        Write-Host "ERROR: $ASSET did not unpack to $APP_NAME. Nothing was installed."
        exit 1
    }
    if (-not $IS_WINDOWS) {
        & chmod +x $tempExe
        if ($LASTEXITCODE -ne 0) { throw "chmod failed with exit code $LASTEXITCODE" }
    }
    # The bundle's own exit code is the only contract-grade answer to "will this
    # run here": a missing glibc loader and a glibc older than the build baseline
    # both surface as a failed exec, without parsing any command's output. Run it
    # on the extracted copy so a failure leaves the existing install intact.
    # Read the code deliberately: PS 7.3+ can promote a native failure to an
    # error under Stop, and an image the OS refuses to start throws outright --
    # both must still land on the message that explains what happened.
    $ErrorActionPreference = "Continue"
    try {
        & $tempExe --version
        $started = ($LASTEXITCODE -eq 0)
    }
    catch {
        $started = $false
    }
    $ErrorActionPreference = "Stop"
    if (-not $started) {
        Write-Host "ERROR: $TAG did not start on this system ($TRIPLE); the existing install was left untouched."
        Write-Host "Hint: the glibc floor each build needs is listed in the README platform matrix."
        Write-Host "Hint: install from PyPI instead: uv tool install uiautomator2-mcp-server"
        exit 1
    }

    Write-Host "[5/5] Installing to $BUNDLE_DIR..."
    if (Test-Path $BUNDLE_DIR) {
        Remove-Item -Path $BUNDLE_DIR -Recurse -Force
    }
    New-Item -ItemType Directory -Path $BUNDLE_DIR -Force | Out-Null
    # The command entry lives in BIN_DIR, which is a child of the bundle on
    # Windows and ~/.local/bin elsewhere; neither is guaranteed to exist yet.
    New-Item -ItemType Directory -Path $BIN_DIR -Force | Out-Null
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
# The bundle itself already ran from the temp dir, so this only proves the
# command entry just created here reaches it.
$ErrorActionPreference = "Continue"
try {
    & $COMMAND_PATH --version
    $commandStarted = ($LASTEXITCODE -eq 0)
}
catch {
    $commandStarted = $false
}
$ErrorActionPreference = "Stop"
if (-not $commandStarted) {
    Write-Host "ERROR: the $APP_NAME command did not run. Try directly:"
    Write-Host "  $COMMAND_PATH --version"
    exit 1
}
if ($null -eq (Get-Command $APP_NAME -ErrorAction SilentlyContinue)) {
    Write-Host "Note: add $BIN_DIR to your PATH to use the `"$APP_NAME`" command."
}

Write-Host ""
Write-Host "To uninstall:"
Write-Host "  Remove-Item -Path `"$BUNDLE_DIR`" -Recurse -Force; Remove-Item -Path `"$COMMAND_PATH`" -Force"
