from __future__ import annotations

from typing import Literal

from anyio import to_thread

from ..mcp import mcp
from .device import get_device

__all__ = (
    "set_orientation",
    "get_orientation",
    "open_notification",
    "open_quick_settings",
    "unlock",
)


OrientationType = Literal["natural", "left", "right", "upsidedown"]


@mcp.tool("set_orientation", tags={"system:orientation"})
async def set_orientation(serial: str, orientation: OrientationType):
    """Set device screen orientation.

    Args:
        serial: Android device serial number.
        orientation: Target orientation, one of natural, left, right, upsidedown.
    """
    async with get_device(serial) as device:
        await to_thread.run_sync(device.set_orientation, orientation)


@mcp.tool("get_orientation", tags={"system:orientation"})
async def get_orientation(serial: str) -> str:
    """Get current device screen orientation.

    Args:
        serial: Android device serial number.

    Returns:
        str: Current orientation, one of natural, left, right, upsidedown, or unknown.
    """
    async with get_device(serial) as device:
        info = await to_thread.run_sync(lambda: device.info)
        return info.get("orientation", "unknown")


@mcp.tool("open_notification", tags={"system:ui"})
async def open_notification(serial: str):
    """Open the notification panel.

    Args:
        serial: Android device serial number.
    """
    async with get_device(serial) as device:
        await to_thread.run_sync(device.open_notification)


@mcp.tool("open_quick_settings", tags={"system:ui"})
async def open_quick_settings(serial: str):
    """Open the quick settings panel.

    Args:
        serial: Android device serial number.
    """
    async with get_device(serial) as device:
        await to_thread.run_sync(device.open_quick_settings)


@mcp.tool("unlock", tags={"system:ui"})
async def unlock(serial: str):
    """Unlock the device screen. Simulates swipe up from the bottom.

    For devices with secure lock like PIN, pattern, or password,
    this only brings up the lock screen.

    Args:
        serial: Android device serial number.
    """
    async with get_device(serial) as device:
        await to_thread.run_sync(device.unlock)
