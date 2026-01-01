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
    global _devices
    device: u2.Device | None = None

    if device := _devices.get(serial):
        # Found, then check if it's still connected
        try:
            device.info
        except u2.ConnectError:
            del _devices[serial]
        else:
            return device.device_info

    device = u2.connect(serial)
    _devices[serial] = device
    return device.device_info
