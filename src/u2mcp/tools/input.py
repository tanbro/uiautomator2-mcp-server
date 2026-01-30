from __future__ import annotations

from anyio import to_thread

from ..mcp import mcp
from .device import get_device

__all__ = (
    "send_text",
    "clear_text",
    "hide_keyboard",
)


@mcp.tool("send_text", tags={"input:text"})
async def send_text(serial: str, text: str, clear: bool = False):
    """Send text to the current input field

    Args:
        serial (str): Android device serialno
        text (str): input text
            clear: clear text before input
    """
    async with get_device(serial) as device:
        await to_thread.run_sync(device.send_keys, text, clear)


@mcp.tool("clear_text", tags={"input:text"})
async def clear_text(serial: str):
    """Clear text in the current input field

    Args:
        serial (str): Android device serialno
    """
    async with get_device(serial) as device:
        await to_thread.run_sync(device.clear_text)


@mcp.tool("hide_keyboard", tags={"input:keyboard"})
async def hide_keyboard(serial: str):
    """Hide keyboard

    Args:
        serial (str): Android device serialno
    """
    async with get_device(serial) as device:
        await to_thread.run_sync(device.hide_keyboard)
