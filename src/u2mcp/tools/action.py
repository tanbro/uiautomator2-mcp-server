from __future__ import annotations

from anyio import to_thread

from ..mcp import mcp
from .device import get_device

__all__ = (
    "click",
    "long_click",
    "double_click",
    "swipe",
    "swipe_points",
    "drag",
    "press_key",
    "screen_on",
    "screen_off",
)


@mcp.tool("click", tags={"action:touch"})
async def click(serial: str, x: int, y: int):
    """Click at specific coordinates

    Args:
        serial (str): Android device serialno
        x (int): X coordinate
        y (int): Y coordinate
    """
    async with get_device(serial) as device:
        await to_thread.run_sync(device.click, x, y)


@mcp.tool("long_click", tags={"action:touch"})
async def long_click(serial: str, x: int, y: int, duration: float = 0.5):
    """Long click at specific coordinates

    Args:
        serial (str): Android device serialno
        x (int): X coordinate
        y (int): Y coordinate
        duration (float): Duration of the long click in seconds, default is 0.5
    """
    async with get_device(serial) as device:
        await to_thread.run_sync(device.long_click, x, y, duration)


@mcp.tool("double_click", tags={"action:touch"})
async def double_click(serial: str, x: int, y: int, duration: float = 0.1):
    """Double click at specific coordinates

    Args:
        serial (str): Android device serialno
        x (int): X coordinate
        y (int): Y coordinate
        duration (float): Duration between clicks in seconds, default is 0.1
    """
    async with get_device(serial) as device:
        await to_thread.run_sync(device.double_click, x, y, duration)


@mcp.tool("swipe", tags={"action:gesture"})
async def swipe(serial: str, fx: int, fy: int, tx: int, ty: int, duration: float = 0.0, step: int = 0):
    """Swipe from one point to another

    Args:
        serial (str): Android device serialno
        fx (int): From position X coordinate
        fy (int): From position Y coordinate
        tx (int): To position X coordinate
        ty (int): To position Y coordinate
        duration (float): duration
        steps: 1 steps is about 5ms, if set, duration will be ignore
    """
    async with get_device(serial) as device:
        await to_thread.run_sync(device.swipe, fx, fy, tx, ty, duration if duration > 0 else None, step if step > 0 else None)


@mcp.tool("swipe_points", tags={"action:gesture"})
async def swipe_points(serial: str, points: list[tuple[int, int]], duration: float = 0.5):
    """Swipe through multiple points

    Args:
        serial (str): Android device serialno
        points (list[tuple[int, int]]): List of (x, y) coordinates to swipe through
        duration (float): Duration of swipe in seconds, default is 0.5
    """
    async with get_device(serial) as device:
        await to_thread.run_sync(device.swipe_points, points, duration)


@mcp.tool("drag", tags={"action:gesture"})
async def drag(serial: str, sx: int, sy: int, ex: int, ey: int, duration: float = 0.5):
    """Swipe from one point to another point.

    Args:
        serial (str): Android device serialno
        sx (int): Start X coordinate
        sy (int): Start Y coordinate
        ex (int): End X coordinate
        ey (int): End Y coordinate
        duration (float): Duration of drag in seconds, default is 0.5
    """
    async with get_device(serial) as device:
        await to_thread.run_sync(device.drag, sx, sy, ex, ey, duration)


@mcp.tool("press_key", tags={"action:key"})
async def press_key(serial: str, key: str):
    """Press a key

    Args:
        serial (str): Android device serialno
        key (str): Key to press.
            Supported key name includes:
            home, back, left, right, up, down, center, menu, search, enter,
            delete(or del), recent(recent apps), volume_up, volume_down,
            volume_mute, camera, power
    """
    async with get_device(serial) as device:
        await to_thread.run_sync(device.press, key)


@mcp.tool("screen_on", tags={"action:screen"})
async def screen_on(serial: str):
    """Turn screen on

    Args:
        serial (str): Android device serialno
    """
    async with get_device(serial) as device:
        await to_thread.run_sync(device.screen_on)


@mcp.tool("screen_off", tags={"action:screen"})
async def screen_off(serial: str):
    """Turn screen off

    Args:
        serial (str): Android device serialno
    """
    async with get_device(serial) as device:
        await to_thread.run_sync(device.screen_off)
