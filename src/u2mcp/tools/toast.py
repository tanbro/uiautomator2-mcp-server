from __future__ import annotations

from anyio import to_thread

from ..mcp import mcp
from .device import get_device

__all__ = (
    "get_toast",
    "show_toast",
    "reset_toast",
)


@mcp.tool("get_toast", tags={"toast:query"})
async def get_toast(serial: str, wait_timeout: float = 10) -> str | None:
    """Get the most recent Android Toast message from the device.

    Toast is a brief notification message in the Android system,
    typically used for operation feedback. This tool uses uiautomator2's
    built-in toast detection via jsonrpc.getLastToast() which is more
    reliable than XPath-based UI hierarchy queries.

    Args:
        serial (str): Android device serial number.
        wait_timeout (float): Maximum time to wait for a Toast message (seconds).

    Returns:
        None or toast message
    """
    async with get_device(serial) as device:
        return await to_thread.run_sync(
            lambda: device.toast.get_message(wait_timeout=wait_timeout)  # type: ignore[arg-type]
        )


@mcp.tool("show_toast", tags={"toast:action"})
async def show_toast(serial: str, text: str, duration: float = 1.0):
    """Display a Toast message on the Android device.

    Args:
        serial (str): Android device serial number.
        text (str): The message text to display in the Toast.
        duration (float): Display duration in seconds (default: 1.0).
    """
    async with get_device(serial) as device:
        await to_thread.run_sync(lambda: device.toast.show(text, duration))


@mcp.tool("reset_toast", tags={"toast:action"})
async def reset_toast(serial: str):
    """Clear the cached Toast message on the device.

    This resets the Toast message cache on the Android device,
    allowing you to wait for new Toast messages without interference
    from previous ones.

    Args:
        serial (str): Android device serial number.
    """
    async with get_device(serial) as device:
        await to_thread.run_sync(lambda: device.toast.reset())
