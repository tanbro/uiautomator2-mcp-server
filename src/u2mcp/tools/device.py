from __future__ import annotations

from typing import Any

import uiautomator2 as u2
from adbutils import adb

from ..mcp import mcp

__all__ = ("device_list", "connect")


_devices: dict[str, u2.Device] = {}


def get_device(serial: str) -> u2.Device:
    return _devices[serial]


@mcp.tool("device_list")
def device_list() -> list[dict[str, Any]]:
    return [d.info for d in adb.device_list()]


@mcp.tool("connect")
def connect(serial: str):
    """Connect to an Android device

    Args:
        serial (str): Android device serialno

    Returns:
        dict[str,Any]: Device information
    """
    d = u2.connect(serial)
    global _devices
    _devices[serial] = d
    return d.info
