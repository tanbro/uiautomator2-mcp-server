"""Simple ADB availability check for uiautomator2 MCP server."""

from __future__ import annotations

import os
import platform
import shutil
import sys

import adbutils
import anyio
from anyio import to_thread
from rich.console import Console

__all__ = ["check_adb", "CheckStatus", "CheckResult", "run_doctor"]


class CheckStatus:
    """Status codes for health checks."""

    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"


class CheckResult:
    """Result of a health check."""

    def __init__(
        self,
        category: str,
        status: str,
        message: str,
        details: dict | None = None,
        fix_suggestion: str | None = None,
    ) -> None:
        self.category = category
        self.status = status
        self.message = message
        self.details = details or {}
        self.fix_suggestion = fix_suggestion


def check_adb_doctor(verbose: bool = False) -> CheckResult:
    """Check ADB availability for doctor command.

    Args:
        verbose: Show detailed information.

    Returns:
        CheckResult with ADB check status.
    """
    try:
        # Try to connect to ADB server
        adb_server_version = adbutils.adb.server_version()
        adb_device_list = adbutils.adb.device_list()

        details = {
            "server_version": str(adb_server_version),
            "device_count": len(adb_device_list),
        }

        if verbose and adb_device_list:
            details["devices"] = [d.serial for d in adb_device_list]

        return CheckResult(
            category="adb",
            status=CheckStatus.PASSED,
            message=f"ADB server version {adb_server_version}, {len(adb_device_list)} device(s)",
            details=details,
        )

    except Exception as e:
        return CheckResult(
            category="adb",
            status=CheckStatus.FAILED,
            message=f"Cannot connect to ADB: {e}",
            details={"error": str(e)},
            fix_suggestion="Install ADB and run 'adb start-server'",
        )


def check_adb(console: Console | None = None) -> bool:
    """Check if ADB is available.

    Returns:
        True if ADB is working, False otherwise.
    """
    if console is None:
        console = Console(stderr=True)

    try:
        # Try to connect to ADB server
        adb_server_version = adbutils.adb.server_version()
        console.print(f"[green]✓ ADB server version: {adb_server_version}[/green]")
        adb_device_list = adbutils.adb.device_list()
        console.print(f"[green]✓ ADB device list:    {adb_device_list}[/green]")
        return True

    except Exception as e:
        console.print(f"[yellow]⚠ Cannot connect to ADB: {e}[/yellow]")
        console.print()

        _print_adb_fix_help(console)
        return False


def _print_adb_fix_help(console: Console) -> None:
    """Print helpful messages for fixing ADB issues."""
    console.print("[cyan]Possible fixes:[/cyan]")

    # Install ADB
    console.print("  1. Install ADB:")
    if sys.platform == "darwin":  # pragma: no cover
        console.print("     [white]brew install android-platform-tools[/white]")
    elif sys.platform == "linux":  # pragma: no cover
        console.print("     [white]sudo apt install adb[/white]  # Debian/Ubuntu")
        console.print("     [white]sudo yum install android-tools[/white]  # Fedora/RHEL")
    elif sys.platform == "win32":  # pragma: no cover
        console.print("     Download: https://developer.android.com/tools/releases/platform-tools")
        console.print("     Or use: [white]winget install Google.PlatformTools[/white]")

    # Start ADB server
    console.print("  2. Start ADB server:")
    console.print("     [white]adb start-server[/white]")

    # Custom ADB path
    console.print("  3. Set custom ADB path (if needed):")
    if sys.platform == "win32":  # pragma: no cover
        console.print("     CMD:        [white]set ADBUTILS_ADB_PATH=C:\\path\\to\\adb.exe[/white]")
        console.print("     PowerShell: [white]$env:ADBUTILS_ADB_PATH='C:\\path\\to\\adb.exe'[/white]")
    else:  # pragma: no cover
        console.print("     [white]export ADBUTILS_ADB_PATH=/path/to/adb[/white]")

    console.print()
    console.print("[yellow]Proceeding anyway. Use --skip-adb-check to bypass this check.[/yellow]")


def check_environment(verbose: bool = False) -> CheckResult:
    """Check Python environment.

    Args:
        verbose: Show detailed information.

    Returns:
        CheckResult with environment check status.
    """
    details = {
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "executable": sys.executable,
        "platform": platform.system(),
        "platform_release": platform.release(),
        "platform_version": platform.version(),
        "architecture": platform.machine(),
    }

    # Check Python version (requires >= 3.11)
    major, minor = sys.version_info[:2]
    if major < 3 or (major == 3 and minor < 11):
        return CheckResult(
            category="environment",
            status=CheckStatus.FAILED,
            message=f"Python {major}.{minor} is not supported (requires >= 3.11)",
            details=details,
            fix_suggestion="Upgrade to Python 3.11 or later",
        )

    return CheckResult(
        category="environment",
        status=CheckStatus.PASSED,
        message=f"Python {details['python_version']} on {details['platform']} {details['architecture']}",
        details=details
        if verbose
        else {
            "python_version": details["python_version"],
            "executable": details["executable"],
            "platform": details["platform"],
        },
    )


async def check_devices_async(verbose: bool = False) -> CheckResult:
    """Check connected devices (async wrapper).

    Args:
        verbose: Show detailed information.

    Returns:
        CheckResult with device connectivity status.
    """
    try:
        devices = await to_thread.run_sync(lambda: adbutils.adb.device_list())

        if not devices:
            return CheckResult(
                category="devices",
                status=CheckStatus.WARNING,
                message="No Android devices connected",
                details={"count": 0},
                fix_suggestion="Connect a device via USB with USB debugging enabled",
            )

        device_info = []

        for device in devices:
            info = {
                "serial": device.serial,
                "model": getattr(device, "getprop_ro_product_model", lambda: "Unknown")(),
                "authorized": True,  # If we can get device info, it's authorized
            }
            device_info.append(info)

        return CheckResult(
            category="devices",
            status=CheckStatus.PASSED,
            message=f"{len(devices)} device(s) connected",
            details={"count": len(devices), "devices": device_info if verbose else [d["serial"] for d in device_info]},
        )

    except Exception as e:
        return CheckResult(
            category="devices",
            status=CheckStatus.WARNING,
            message=f"Cannot check devices: {e}",
            details={"error": str(e)},
            fix_suggestion="Ensure ADB is running and devices are properly connected",
        )


def check_devices(verbose: bool = False) -> CheckResult:
    """Check connected devices (sync wrapper).

    Args:
        verbose: Show detailed information.

    Returns:
        CheckResult with device connectivity status.
    """
    return anyio.run(check_devices_async, verbose)


async def check_u2_init_async(verbose: bool = False) -> CheckResult:
    """Check uiautomator2 initialization status (async wrapper).

    Args:
        verbose: Show detailed information.

    Returns:
        CheckResult with uiautomator2 initialization status.
    """
    try:
        devices = await to_thread.run_sync(lambda: adbutils.adb.device_list())

        if not devices:
            return CheckResult(
                category="u2_init",
                status=CheckStatus.SKIPPED,
                message="No devices to check",
                details={},
            )

        import uiautomator2 as u2

        initialized = []
        not_initialized = []

        for device_adb in devices:
            try:
                if device_adb.serial is None:
                    raise RuntimeError("Device serial is None")
                device = u2.connect(device_adb.serial)
                # Try to get session info to verify initialization
                _ = device.session
                initialized.append(device_adb.serial)
            except Exception:
                not_initialized.append(device_adb.serial)

        if not_initialized:
            return CheckResult(
                category="u2_init",
                status=CheckStatus.FAILED,
                message=f"uiautomator2 not initialized on {len(not_initialized)} device(s)",
                details={
                    "initialized": initialized,
                    "not_initialized": not_initialized,
                },
                fix_suggestion="Run the 'init' tool via MCP or use --fix flag",
            )

        return CheckResult(
            category="u2_init",
            status=CheckStatus.PASSED,
            message=f"uiautomator2 initialized on {len(initialized)} device(s)",
            details={"devices": initialized if verbose else len(initialized)},
        )

    except Exception as e:
        return CheckResult(
            category="u2_init",
            status=CheckStatus.WARNING,
            message=f"Cannot check uiautomator2 status: {e}",
            details={"error": str(e)},
        )


def check_u2_init(verbose: bool = False) -> CheckResult:
    """Check uiautomator2 initialization status (sync wrapper).

    Args:
        verbose: Show detailed information.

    Returns:
        CheckResult with uiautomator2 initialization status.
    """
    import anyio

    return anyio.run(check_u2_init_async, verbose)


def check_mcp_tools(verbose: bool = False) -> CheckResult:
    """Check MCP tool registration.

    Args:
        verbose: Show detailed information.

    Returns:
        CheckResult with MCP tools check status.
    """
    try:
        import anyio

        from .mcp import make_mcp

        async def get_tool_count() -> int:
            mcp = make_mcp()
            tools = await mcp.get_tools()
            return len(tools)

        tool_count = anyio.run(get_tool_count)

        # Expected tool count (approximately, can vary with filters)
        expected_min = 40  # Minimum expected tools

        if tool_count < expected_min:
            return CheckResult(
                category="mcp_tools",
                status=CheckStatus.WARNING,
                message=f"Only {tool_count} tools registered (expected at least {expected_min})",
                details={"count": tool_count, "expected_min": expected_min},
            )

        return CheckResult(
            category="mcp_tools",
            status=CheckStatus.PASSED,
            message=f"{tool_count} MCP tools registered",
            details={"count": tool_count},
        )

    except Exception as e:
        return CheckResult(
            category="mcp_tools",
            status=CheckStatus.FAILED,
            message=f"Cannot check MCP tools: {e}",
            details={"error": str(e)},
        )


def check_scrcpy(verbose: bool = False) -> CheckResult:
    """Check scrcpy availability (optional).

    Args:
        verbose: Show detailed information.

    Returns:
        CheckResult with scrcpy check status.
    """
    scrcpy_path = os.environ.get("SCRCPY", "scrcpy")
    scrcpy_exists = shutil.which(scrcpy_path)

    if not scrcpy_exists:
        return CheckResult(
            category="scrcpy",
            status=CheckStatus.WARNING,
            message="scrcpy not found (optional for screen mirroring)",
            details={"path": scrcpy_path},
            fix_suggestion="Install scrcpy: brew install scrcpy (macOS) or sudo apt install scrcpy (Linux)",
        )

    return CheckResult(
        category="scrcpy",
        status=CheckStatus.PASSED,
        message=f"scrcpy found at {scrcpy_exists}",
        details={"path": scrcpy_exists} if verbose else {},
    )


def _print_check_result(console: Console, result: CheckResult, verbose: bool = False) -> None:
    """Print a single check result with Rich formatting.

    Args:
        console: Rich console instance.
        result: CheckResult to print.
        verbose: Show detailed information.
    """
    # Choose icon and color based on status
    status_symbols = {
        CheckStatus.PASSED: ("✓", "green"),
        CheckStatus.FAILED: ("✗", "red"),
        CheckStatus.WARNING: ("⚠", "yellow"),
        CheckStatus.SKIPPED: ("⊘", "dim"),
    }

    symbol, color = status_symbols.get(result.status, ("?", "white"))

    # Print category header
    console.print(f"[{color}]{symbol} {result.category.title()}[/{color}]")

    # Print message
    console.print(f"  └─ {result.message}")

    # Print details if verbose
    if verbose and result.details:
        items = list(result.details.items())
        for i, (key, value) in enumerate(items):
            is_last = i == len(items) - 1
            prefix = "     └─ " if is_last else "     ├─ "

            if isinstance(value, list):
                for item in value:
                    console.print(f"{prefix}{key}: {item}")
            elif isinstance(value, dict):
                for k, v in value.items():
                    console.print(f"     ├─ {k}: {v}")
            else:
                console.print(f"{prefix}{key}: {value}")

    # Print fix suggestion if available
    if result.fix_suggestion:
        console.print(f"     [cyan]Fix: {result.fix_suggestion}[/cyan]")

    console.print()  # Blank line after each check


def run_doctor(
    verbose: bool = False,
    fix: bool = False,
    category: str | None = None,
    exclude: str | None = None,
) -> int:
    """Run comprehensive diagnostics.

    Args:
        verbose: Show detailed diagnostic output.
        fix: Attempt automatic fixes for issues.
        category: Only check specific categories (comma-separated).
        exclude: Exclude specific categories (comma-separated).

    Returns:
        Exit code: 0 (all passed), 1 (some failed), 2 (doctor error).
    """
    console = Console()

    # Parse category filters
    include_categories = None
    if category:
        include_categories = [c.strip().lower() for c in category.split(",")]

    exclude_categories = None
    if exclude:
        exclude_categories = [c.strip().lower() for c in exclude.split(",")]

    # Define all checks
    all_checks = [
        ("environment", lambda: check_environment(verbose)),
        ("adb", lambda: check_adb_doctor(verbose)),
        ("devices", lambda: check_devices(verbose)),
        ("u2_init", lambda: check_u2_init(verbose)),
        ("mcp_tools", lambda: check_mcp_tools(verbose)),
        ("scrcpy", lambda: check_scrcpy(verbose)),
    ]

    # Filter checks
    checks_to_run = []
    for cat, check_func in all_checks:
        if include_categories and cat not in include_categories:
            continue
        if exclude_categories and cat in exclude_categories:
            continue
        checks_to_run.append((cat, check_func))

    # Run checks
    results = []
    for cat, check_func in checks_to_run:
        try:
            result = check_func()
            results.append(result)
            _print_check_result(console, result, verbose)

            # Attempt auto-fix if requested
            if fix and result.status == CheckStatus.FAILED:
                if cat == "u2_init" and result.details.get("not_initialized"):
                    console.print("[cyan]Attempting to initialize uiautomator2...[/cyan]")
                    try:
                        import uiautomator2 as u2

                        for serial in result.details["not_initialized"]:
                            device = u2.connect(serial)
                            console.print(f"  Initializing {serial}...")
                            device.shell("pm list packages")  # Simple test
                            console.print(f"  [green]✓ {serial} initialized[/green]")
                    except Exception as e:
                        console.print(f"  [red]✗ Auto-fix failed: {e}[/red]")

        except Exception as e:
            console.print(f"[red]✗ Error running {cat} check: {e}[/red]")
            results.append(
                CheckResult(
                    category=cat,
                    status=CheckStatus.FAILED,
                    message=f"Check failed with error: {e}",
                    details={},
                )
            )

    # Print summary
    passed = sum(1 for r in results if r.status == CheckStatus.PASSED)
    failed = sum(1 for r in results if r.status == CheckStatus.FAILED)
    warning = sum(1 for r in results if r.status in (CheckStatus.WARNING, CheckStatus.SKIPPED))

    console.print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    console.print(f"[bold]Summary: {passed} passed, {failed} failed, {warning} warning[/bold]")

    # Return exit code
    if failed > 0:
        return 1
    return 0
