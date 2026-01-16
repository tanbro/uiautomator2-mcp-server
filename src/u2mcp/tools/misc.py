from __future__ import annotations

import anyio

from ..mcp import mcp

__all__ = ("delay",)


@mcp.tool("delay")
async def delay(seconds: float):
    """Delay for a specific amount of time

    Args:
        seconds(float): Delay duration in seconds
    """
    await anyio.sleep(seconds)
