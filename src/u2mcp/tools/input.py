from __future__ import annotations

from anyio import to_thread

from ..mcp import mcp
from .device import get_device

__all__ = (
    "send_text",
    "set_focused_text",
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


@mcp.tool("set_focused_text", tags={"input:text"})
async def set_focused_text(serial: str, text: str) -> bool:
    """Set text to the currently focused input element.

    This method uses device(focused=True).set_text() which calls jsonrpc.setText()
    directly, bypassing IME requirements. Works on devices with IME restrictions
    (e.g., OPPO/ColorOS).

    Args:
        serial (str): Android device serialno
        text (str): Text to set in the focused element

    Returns:
        bool: True if text was set successfully

    Raises:
        RuntimeError: If no element is currently focused
    """
    async with get_device(serial) as device:
        return await to_thread.run_sync(lambda: device(focused=True).set_text(text))


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
