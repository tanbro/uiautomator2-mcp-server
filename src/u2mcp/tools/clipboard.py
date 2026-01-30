from __future__ import annotations

from anyio import to_thread

from ..mcp import mcp
from .device import get_device

__all__ = ("read_clipboard", "write_clipboard")


@mcp.tool("read_clipboard", tags={"clipboard:read"})
async def read_clipboard(serial: str) -> str | None:
    """Read clipboard from device

    Args:
        serial (str): Android device serialno

    Returns:
        str: The actual text in the clip.
        None: If there is no text in the clip.
    """
    async with get_device(serial) as device:
        return await to_thread.run_sync(lambda: device.clipboard)


@mcp.tool("write_clipboard", tags={"clipboard:write"})
async def write_clipboard(serial: str, text: str):
    """Write clipboard to device

    Args:
        serial (str): Android device serialno
        text: The actual text in the clip.
    """
    async with get_device(serial) as device:
        await to_thread.run_sync(device.set_clipboard, text)
