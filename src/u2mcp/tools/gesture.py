from __future__ import annotations

from anyio import to_thread

from ..mcp import mcp
from .device import get_device

__all__ = (
    "swipe_ext",
    "swipe_left",
    "swipe_right",
    "swipe_up",
    "swipe_down",
)


async def _swipe_ext_impl(serial: str, direction: str, scale: float):
    """Internal implementation for swipe from screen edge."""
    async with get_device(serial) as device:
        await to_thread.run_sync(device.swipe_ext, direction, scale)


@mcp.tool("swipe_ext", tags={"gesture:edge"})
async def swipe_ext(serial: str, direction: str, scale: float):
    """Swipe from screen edge.

    Args:
        serial (str): Android device serial number.
        direction (str): Swipe direction, one of left, right, up, down.
        scale (float): Percentage of swipe distance from edge, range (0, 1.0).
    """
    await _swipe_ext_impl(serial, direction, scale)


@mcp.tool("swipe_left", tags={"gesture:edge"})
async def swipe_left(serial: str, scale: float):
    """Swipe from right edge to left.

    Args:
        serial (str): Android device serial number.
        scale (float): Percentage of swipe distance from edge, range (0, 1.0).
    """
    await _swipe_ext_impl(serial, "left", scale)


@mcp.tool("swipe_right", tags={"gesture:edge"})
async def swipe_right(serial: str, scale: float):
    """Swipe from left edge to right.

    Args:
        serial (str): Android device serial number.
        scale (float): Percentage of swipe distance from edge, range (0, 1.0).
    """
    await _swipe_ext_impl(serial, "right", scale)


@mcp.tool("swipe_up", tags={"gesture:edge"})
async def swipe_up(serial: str, scale: float):
    """Swipe from bottom edge to top.

    Args:
        serial (str): Android device serial number.
        scale (float): Percentage of swipe distance from edge, range (0, 1.0).
    """
    await _swipe_ext_impl(serial, "up", scale)


@mcp.tool("swipe_down", tags={"gesture:edge"})
async def swipe_down(serial: str, scale: float):
    """Swipe from top edge to bottom.

    Args:
        serial (str): Android device serial number.
        scale (float): Percentage of swipe distance from edge, range (0, 1.0).
    """
    await _swipe_ext_impl(serial, "down", scale)
