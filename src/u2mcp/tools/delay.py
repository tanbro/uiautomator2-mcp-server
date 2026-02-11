from __future__ import annotations

import anyio

from ..mcp import mcp

__all__ = ("delay",)


@mcp.tool("delay", tags={"util:delay"})
async def delay(seconds: float) -> None:
    """Delay for a specific amount of time.

    Args:
        seconds: Delay duration in seconds.
    """
    await anyio.sleep(seconds)
