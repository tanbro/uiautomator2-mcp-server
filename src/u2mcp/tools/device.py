from __future__ import annotations

import asyncio
import sys
from base64 import b64encode
from contextlib import asynccontextmanager
from io import BytesIO
from typing import Any, Literal

import uiautomator2 as u2
from adbutils import adb
from fastmcp.dependencies import CurrentContext
from fastmcp.server.context import Context
from fastmcp.utilities.logging import get_logger
from PIL.Image import Image

from ..mcp import mcp

__all__ = ("device_list", "init", "connect", "window_size", "screenshot", "dump_hierarchy")


StdoutType = Literal["stdout", "stderr"]

_devices: dict[str, tuple[asyncio.Semaphore, u2.Device]] = {}
_device_connect_lock = asyncio.Lock()


@asynccontextmanager
async def get_device(serial: str):
    async with _device_connect_lock:
        try:
            semaphore, device = _devices[serial]
        except KeyError:

            def _connect():
                _d = u2.connect(serial)
                _d.info
                return _d

            device = await asyncio.to_thread(_connect)
            semaphore = asyncio.Semaphore()
            _devices[serial] = semaphore, device
    async with semaphore:
        yield device


@mcp.tool("device_list")
async def device_list() -> list[dict[str, Any]]:
    device_list = await asyncio.to_thread(adb.device_list)
    return [d.info for d in device_list]


@mcp.tool("init")
async def init(serial: str = "", ctx: Context = CurrentContext()):
    """Install essential resources to device.

    Important:
        This tool must be run on the Android device before running operation actions.

    Args:
        serial (str): Android device serialno to initialize. If empty string, all devices will be initialized.

    Returns:
        None upon successful completion (exit code 0).
        Raises an exception if the subprocess returns a non-zero exit code.
    """
    logger = get_logger(f"{__name__}.init")
    args = ["-m", "uiautomator2", "init"]
    if serial := serial.strip():
        args.extend(["--serial", serial])

    logger.info("Running uiautomator2 init command: %s %s", sys.executable, args)
    process = await asyncio.create_subprocess_exec(
        sys.executable, *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    if process.stdout is None:
        raise RuntimeError("stdout is None")
    if process.stderr is None:
        raise RuntimeError("stderr is None")

    output_queue: asyncio.Queue[tuple[StdoutType, str]] = asyncio.Queue()

    async def stream_subprocess(stream: asyncio.streams.StreamReader, tag: StdoutType):
        while True:
            line_bytes = await stream.readline()
            await output_queue.put((tag, line_bytes.decode()))
            if not line_bytes:  # Reached EOF, the empty string is in the queue
                break

    # Start the stream reading tasks
    tasks = [
        asyncio.create_task(coro)
        for coro in (
            stream_subprocess(process.stdout, "stdout"),
            stream_subprocess(process.stderr, "stderr"),
        )
    ]

    completed_streams = 0

    logger.info("read uiautomator2 init command stdio")

    while True:
        tag, line = await output_queue.get()

        if not line:  # This was the EOF sentinel (empty string)
            completed_streams += 1
            if completed_streams == len(tasks):
                output_queue.task_done()
                break  # Both streams are done, exit the main consumer loop

        # Process the actual line data
        if line := line.strip():
            logger.info("%s: %s", tag, line)
            if tag == "stdout":
                await ctx.info(line)
            else:
                await ctx.warning(line)

        output_queue.task_done()

    # Wait for the tasks to formally complete and the process to exit
    logger.info("waiting for uiautomator2 init command to complete")
    await asyncio.gather(*tasks)
    exit_code = await process.wait()
    logger.info("uiautomator2 init command exited with code: %s", exit_code)
    if exit_code != 0:
        raise RuntimeError(f"uiautomator2 init command exited with non-zero code: {exit_code}")


@mcp.tool("connect")
async def connect(serial: str = ""):
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
            async with get_device(serial) as device:
                # Found, then check if it's still connected
                try:
                    return await asyncio.to_thread(lambda: device.device_info | device.info)
                except u2.ConnectError as e:
                    # Found, but not connected, delete it
                    logger.warning("Device %s is no longer connected, delete it!", serial)
                    del _devices[serial]
                    raise e from None
        except KeyError:
            # Not found, need a new connection!
            logger.info("Cannot find device with serial %s, connecting...")

    # make new connection here!
    async with _device_connect_lock:
        device = await asyncio.to_thread(u2.connect, serial)
        logger.info("Connected to device %s", device.serial)
        result = await asyncio.to_thread(lambda: device.device_info | device.info)
        _devices[device.serial] = asyncio.Semaphore(), device
        return result


@mcp.tool("disconnect")
async def disconnect(serial: str):
    """Disconnect from an Android device

    Args:
        serial (str): Android device serialno

    Returns:
        None
    """
    if not (serial := serial.strip()):
        raise ValueError("serial cannot be empty")
    async with _device_connect_lock:
        del _devices[serial]


@mcp.tool("disconnect_all")
async def disconnect_all():
    """Disconnect from all Android devices"""
    async with _device_connect_lock:
        _devices.clear()


@mcp.tool("window_size")
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
        width, height = await asyncio.to_thread(device.window_size)
        return {"width": width, "height": height}


@mcp.tool("screenshot")
async def screenshot(serial: str, display_id: int = -1) -> dict[str, Any]:
    """
    Take screenshot of device

    Args:
        serial (str): Android device serialno
        display_id (int): use specific display if device has multiple screen. Defaults to -1.

    Returns:
        dict[str,Any]: Screenshot image JPEG data with the following keys:
            - "image" (str): Base64 encoded image data in data URL format (data:image/jpeg;base64,...)
            - "size" (tuple[int,int]): Image dimensions as (width, height)
    """
    display_id = int(display_id)
    async with get_device(serial) as device:
        im = await asyncio.to_thread(
            device.screenshot,
            display_id=display_id if display_id >= 0 else None,
        )  # type: ignore[arg-type]

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


@mcp.tool("dump_hierarchy")
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
        return await asyncio.to_thread(
            device.dump_hierarchy, compressed=compressed, pretty=pretty, max_depth=max_depth if max_depth > 0 else None
        )


@mcp.tool("info")
async def info(serial: str) -> dict[str, Any]:
    """
    Get device info

    Args:
        serial (str): Android device serialno

    Returns:
        dict[str,Any]: Device info
    """

    async with get_device(serial) as device:
        return await asyncio.to_thread(lambda: device.info)
