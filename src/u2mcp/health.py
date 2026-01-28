"""Simple ADB availability check for uiautomator2 MCP server."""

from __future__ import annotations

import sys

from rich.console import Console

__all__ = ["check_adb"]


def check_adb(console: Console | None = None) -> bool:
    """Check if ADB is available.

    Returns:
        True if ADB is working, False otherwise.
    """
    if console is None:
        console = Console(stderr=True)

    try:
        import adbutils

        # Try to connect to ADB server
        adbutils.adb.server_version()
        console.print(f"[green]✓ ADB server version: {adbutils.adb.server_version()}[/green]")
        console.print(f"[green]✓ ADB device list:    {adbutils.adb.device_list()}[/green]")
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
    if sys.platform == "darwin":
        console.print("     [white]brew install android-platform-tools[/white]")
    elif sys.platform == "linux":
        console.print("     [white]sudo apt install adb[/white]  # Debian/Ubuntu")
        console.print("     [white]sudo yum install android-tools[/white]  # Fedora/RHEL")
    elif sys.platform == "win32":
        console.print("     Download: https://developer.android.com/tools/releases/platform-tools")
        console.print("     Or use: [white]winget install Google.PlatformTools[/white]")

    # Start ADB server
    console.print("  2. Start ADB server:")
    console.print("     [white]adb start-server[/white]")

    # Custom ADB path
    console.print("  3. Set custom ADB path (if needed):")
    if sys.platform == "win32":
        console.print("     CMD:        [white]set ADBUTILS_ADB_PATH=C:\\path\\to\\adb.exe[/white]")
        console.print("     PowerShell: [white]$env:ADBUTILS_ADB_PATH='C:\\path\\to\\adb.exe'[/white]")
    else:
        console.print("     [white]export ADBUTILS_ADB_PATH=/path/to/adb[/white]")

    console.print()
    console.print("[yellow]Proceeding anyway. Use --skip-adb-check to bypass this check.[/yellow]")
