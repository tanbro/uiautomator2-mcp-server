from __future__ import annotations

import asyncio

from ..mcp import mcp


@mcp.tool("delay")
async def delay(seconds: float):
    """Delay for a specific amount of time

    Args:
        seconds(float): Delay duration in seconds
    """
    await asyncio.sleep(seconds)
