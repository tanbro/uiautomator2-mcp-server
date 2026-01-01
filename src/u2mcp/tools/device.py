from __future__ import annotations

from base64 import b64encode
from io import BytesIO
from typing import Any

import uiautomator2 as u2
from adbutils import adb
from PIL.Image import Image

from ..mcp import mcp

__all__ = ("device_list", "connect", "window_size", "screenshot", "dump_hierarchy")


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


@mcp.tool("window_size")
def window_size(serial: str) -> tuple[int, int]:
    """Get window size of an Android device

    Args:
        serial (str): Android device serialno

    Returns:
        dict[int,int]: Window size (width, height)
    """
    return get_device(serial).window_size()


@mcp.tool("screenshot")
def screenshot(serial: str, display_id: int | None = None) -> dict[str, Any]:
    """
    Take screenshot of device

    Args:
        serial (str): Android device serialno
        display_id (int): use specific display if device has multiple screen

    Returns:
        dict[str,Any]: Screenshot image JPEG data with the following keys:
            - "image" (str): Base64 encoded image data in data URL format (data:image/jpeg;base64,...)
            - "size" (tuple[int, int]): Image dimensions as (width, height)
    """
    device = get_device(serial)
    im: Image = device.screenshot(display_id=display_id)  # type: ignore

    with BytesIO() as fp:
        im.save(fp, "jpeg")
        im_data = fp.getbuffer()

    return {
        "image": "data:image/jpeg;base64," + b64encode(im_data).decode(),
        "size": (im.width, im.height),
    }


@mcp.tool("dump_hierarchy")
def dump_hierarchy(serial: str, compressed=False, pretty=False, max_depth: int | None = None) -> str:
    """
    Dump window hierarchy

    Args:
        serial (str): Android device serialno
        compressed (bool): return compressed xml
        pretty (bool): pretty print xml
        max_depth (int): max depth of hierarchy

    Returns:
        str: xml content
    """
    device = get_device(serial)
    return device.dump_hierarchy(compressed=compressed, pretty=pretty, max_depth=max_depth)
