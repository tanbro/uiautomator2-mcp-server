from __future__ import annotations

import asyncio

from ..mcp import mcp


@mcp.tool("delay")
async def delay(duration: float):
    """Delay for a specific amount of time

    Args:
        duration (float): Duration in seconds
    """
    await asyncio.sleep(duration)
