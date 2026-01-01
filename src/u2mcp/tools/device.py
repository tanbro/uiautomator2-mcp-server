from adbutils import adb

from ..mcp import mcp

__all__ = ["device_list"]


@mcp.tool("device_list")
def device_list():
    return [str(x) for x in adb.device_list()]
