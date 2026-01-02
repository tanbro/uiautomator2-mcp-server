from __future__ import annotations

import asyncio
import sys
from base64 import b64encode
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

_devices: dict[str, u2.Device] = {}


def get_device(serial: str) -> u2.Device:
    return _devices[serial]


@mcp.tool("device_list")
def device_list() -> list[dict[str, Any]]:
    return [d.info for d in adb.device_list()]


@mcp.tool("init")
async def init(serial: str | None = None, ctx: Context = CurrentContext()):
    """Install essential resources to device.

    Important:
        This tool must be run on the Android device before running operation actions.

    Args:
        serial (str): Android device serialno to initialize. If None, all devices will be initialized.

    Returns:
        None upon successful completion (exit code 0).
        Raises an exception if the subprocess returns a non-zero exit code.
    """
    logger = get_logger(f"{__name__}.init")
    args = ["-m", "uiautomator2", "init"]
    if serial:
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
            if tag == "stdout":
                logger.info(line)
                await ctx.info(line)
            else:
                logger.error(line)
                await ctx.error(line)

        output_queue.task_done()

    # Wait for the tasks to formally complete and the process to exit
    logger.info("waiting for uiautomator2 init command to complete")
    await asyncio.gather(*tasks)
    exit_code = await process.wait()
    logger.info("uiautomator2 init command exited with code: %s", exit_code)
    if exit_code != 0:
        raise RuntimeError(f"uiautomator2 init command exited with non-zero code: {exit_code}")


@mcp.tool("connect")
def connect(serial: str | None = None):
    """Connect to an Android device

    Args:
        serial (str|None): Android device serialno. If None, connect the unique device if only one device is connected.

    Returns:
        dict[str,Any]: Device information
    """
    global _devices
    device: u2.Device | None = None

    if serial:
        if device := _devices.get(serial):
            # Found, then check if it's still connected
            try:
                return device.device_info | device.info
            except u2.ConnectError:
                del _devices[serial]
        else:
            device = u2.connect(serial)
            result = device.device_info | device.info
            _devices[serial] = device
            return result

    else:
        device = u2.connect()
        result = device.device_info | device.info
        _devices[device.serial] = device
        return result

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
