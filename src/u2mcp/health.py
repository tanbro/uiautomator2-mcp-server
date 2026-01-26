"""Simple ADB availability check for uiautomator2 MCP server."""

from __future__ import annotations

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
        from adbutils import adb

        # Try to connect to ADB server
        adb.device_list()
        console.print("[green]✓ ADB is available[/green]")
        return True

    except Exception as e:
        console.print(f"[yellow]⚠ Cannot connect to ADB: {e}[/yellow]")
        console.print("  Start ADB server: adb start-server")
        return False
