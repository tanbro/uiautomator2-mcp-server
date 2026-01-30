from __future__ import annotations

import argparse
from base64 import b64encode
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from io import BytesIO
from typing import Any

import uiautomator2 as u2
from adbutils import adb
from anyio import Lock, to_thread
from fastmcp.utilities.logging import get_logger
from PIL.Image import Image

from ..mcp import mcp

__all__ = (
    "device_list",
    "shell_command",
    "init",
    "connect",
    "disconnect",
    "disconnect_all",
    "window_size",
    "screenshot",
    "dump_hierarchy",
    "info",
)


_devices: dict[str, tuple[Lock, u2.Device]] = {}
_global_device_connection_lock = Lock()


@asynccontextmanager
async def get_device(serial: str) -> AsyncGenerator[u2.Device]:
    async with _global_device_connection_lock:
        try:
            lock, device = _devices[serial]
        except KeyError:

            def _connect():
                _d = u2.connect(serial)
                _d.info
                return _d

            device = await to_thread.run_sync(_connect)
            lock = Lock()
            _devices[serial] = lock, device

    async with lock:
        yield device


@mcp.tool("init", tags={"device:manage"})
async def init(serial: str = ""):
    """Install essential resources (minicap, minitouch, uiautomator ...) to device.

    Important:
        This tool must be run on the Android device before running operation actions.

    Args:
        serial (str): Android device serialno to initialize. If empty string, all devices will be initialized.

    Returns:
        None upon successful completion
        Raises an exception if the subprocess returns a non-zero exit code.
    """
    from uiautomator2.__main__ import cmd_init

    args = argparse.Namespace(serial=serial, serial_optional=None)
    return await to_thread.run_sync(cmd_init, args)


@mcp.tool("purge", tags={"device:manage"})
async def purge(serial: str = ""):
    """Purge all resources (minicap, minitouch, uiautomator ...) from device.

    Important:
        This tool must be run on the Android device before running operation actions.

    Args:
        serial (str): Android device serialno to purge. If empty string, all devices will be purged.

    Returns:
        None upon successful completion
        Raises an exception if the subprocess returns a non-zero exit code.
    """
    from uiautomator2.__main__ import cmd_purge

    args = argparse.Namespace(serial=serial)
    return await to_thread.run_sync(cmd_purge, args)


@mcp.tool("shell_command", tags={"device:shell"})
async def shell_command(serial: str, command: str, timeout: float = 60) -> tuple[int, str]:
    """Run a shell command on an Android device

    Args:
        serial (str): Android device serialno
        command (str): Shell command to run
        timeout (float): Seconds to wait for command to complete.

    Returns:
        tuple[int,str]: Return code and output of the command
    """
    async with get_device(serial) as device:
        return_value = await to_thread.run_sync(device.adb_device.shell2, command, timeout)
        return return_value.returncode, return_value.output


@mcp.tool("device_list", tags={"device:info"})
async def device_list() -> list[dict[str, Any]]:
    """List of Adb Device with state:device

    Returns:
        list[dict[str,Any]]: List Adb Device information
    """
    device_list = await to_thread.run_sync(adb.device_list)
    return [d.info for d in device_list]


@mcp.tool("connect", tags={"device:manage"})
async def connect(serial: str = "") -> dict[str, Any]:
    """Connect to an Android device

    Args:
        serial (str): Android device serial number. If empty string, connects to the unique device if only one device is connected.

    Returns:
        dict[str,Any]: Device information
    """
    global _devices
    device: u2.Device | None = None

    logger = get_logger(f"{__name__}.connect")

    if serial := serial.strip():
        try:
            async with get_device(serial) as device_1:
                # Found, then check if it's still connected
                try:
                    return await to_thread.run_sync(lambda: device_1.device_info | device_1.info)
                except u2.ConnectError as e:
                    # Found, but not connected, delete it
                    logger.warning("Device %s is no longer connected, delete it!", serial)
                    del _devices[serial]
                    raise e from None
        except KeyError:
            # Not found, need a new connection!
            logger.info("Cannot find device with serial %s, connecting...")

    # make new connection here!
    async with _global_device_connection_lock:
        device = await to_thread.run_sync(u2.connect, serial)
        if device is None:
            raise RuntimeError("Cannot connect to device")
        logger.info("Connected to device %s", device.serial)
        result = await to_thread.run_sync(lambda: device.device_info | device.info)
        _devices[device.serial] = Lock(), device
        return result


@mcp.tool("disconnect", tags={"device:manage"})
async def disconnect(serial: str):
    """Disconnect from an Android device

    Args:
        serial (str): Android device serialno

    Returns:
        None
    """
    if not (serial := serial.strip()):
        raise ValueError("serial cannot be empty")
    async with _global_device_connection_lock:
        del _devices[serial]


@mcp.tool("disconnect_all", tags={"device:manage"})
async def disconnect_all():
    """Disconnect from all Android devices"""
    async with _global_device_connection_lock:
        _devices.clear()


@mcp.tool("window_size", tags={"device:info"})
async def window_size(serial: str) -> dict[str, int]:
    """Get window size of an Android device

    Args:
        serial (str): Android device serialno

    Returns:
        dict[str,int]: Window size object:
            - "width" (int): Window width
            - "height" (int): Window height
    """
    async with get_device(serial) as device:
        width, height = await to_thread.run_sync(device.window_size)
        return {"width": width, "height": height}


@mcp.tool("screenshot", tags={"device:capture", "screen:capture"})
async def screenshot(serial: str, display_id: int = -1) -> dict[str, Any]:
    """
    Take screenshot of device

    Args:
        serial (str): Android device serialno
        display_id (int): use specific display if device has multiple screen. Defaults to -1.

    Returns:
        dict[str,Any]: Screenshot image JPEG data with the following keys:
            - image (str): Base64 encoded image data in data URL format (data:image/jpeg;base64,...)
            - size (tuple[int,int]): Image dimensions as (width, height)
    """
    display_id = int(display_id)
    async with get_device(serial) as device:
        im = await to_thread.run_sync(lambda: device.screenshot(display_id=display_id if display_id >= 0 else None))

    if not isinstance(im, Image):
        raise RuntimeError("Invalid image")

    with BytesIO() as fp:
        im.save(fp, "jpeg")
        im_data = fp.getvalue()

    return {
        "width": im.width,
        "height": im.height,
        "image": "data:image/jpeg;base64," + b64encode(im_data).decode(),
    }


@mcp.tool("dump_hierarchy", tags={"device:capture"})
async def dump_hierarchy(serial: str, compressed: bool = False, pretty: bool = False, max_depth: int = -1) -> str:
    """
    Dump window hierarchy

    Args:
        serial (str): Android device serialno
        compressed (bool): return compressed xml
        pretty (bool): pretty print xml
        max_depth (int): max depth of hierarchy

    Returns:
        str: xml string of the hierarchy tree
    """
    async with get_device(serial) as device:
        return await to_thread.run_sync(
            lambda: device.dump_hierarchy(compressed=compressed, pretty=pretty, max_depth=max_depth if max_depth > 0 else None)
        )


@mcp.tool("info", tags={"device:info"})
async def info(serial: str) -> dict[str, Any]:
    """
    Get device info

    Args:
        serial (str): Android device serialno

    Returns:
        dict[str,Any]: Device info
    """

    async with get_device(serial) as device:
        return await to_thread.run_sync(lambda: device.info)
