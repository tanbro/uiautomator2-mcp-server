from __future__ import annotations

from anyio import to_thread

from ..mcp import mcp
from .device import get_device

__all__ = ("wait_activity",)


@mcp.tool("wait_activity")
async def wait_activity(serial: str, activity: str, timeout: float = 20.0) -> bool:
    """wait activity

    Args:
        serial (str): Android device serialno
        activity (str): name of activity
        timeout (float): max wait time

    Returns:
        bool of activity
    """
    async with get_device(serial) as device:
        # timeout: float here is actually no problem
        return await to_thread.run_sync(device.wait_activity, activity, timeout)  # type: ignore[arg-type]
