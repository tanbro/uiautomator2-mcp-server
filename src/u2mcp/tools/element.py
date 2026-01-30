from __future__ import annotations

from base64 import b64encode
from io import BytesIO
from typing import Any

from anyio import to_thread
from PIL.Image import Image

from ..mcp import mcp
from .device import get_device

__all__ = (
    "activity_wait",
    "element_wait",
    "element_wait_gone",
    "element_click",
    "element_click_nowait",
    "element_click_until_gone",
    "element_long_click",
    "element_screenshot",
    "element_get_text",
    "element_set_text",
    "element_bounds",
    "element_swipe",
    "element_scroll",
    "element_scroll_to",
)


@mcp.tool("activity_wait", tags={"element:wait"})
async def activity_wait(serial: str, activity: str, timeout: float = 20.0) -> bool:
    """wait activity

    Args:
        serial (str): Android device serialno
        activity (str): name of activity
        timeout (float): max wait time

    Returns:
        bool of activity
    """
    async with get_device(serial) as device:
        # timeout: float here is actually no problem
        return await to_thread.run_sync(device.wait_activity, activity, timeout)  # type: ignore[arg-type]


@mcp.tool("element_wait", tags={"element:wait"})
async def element_wait(serial: str, xpath: str, timeout: float | None = None) -> bool:
    """
    wait until element found

    Args:
        serial (str): Android device serialno
        xpath (str): element xpath
        timeout (Optional float): seconds wait element show up

    Returns:
        bool: if element found
    """
    async with get_device(serial) as device:
        return await to_thread.run_sync(lambda: device.xpath(xpath).wait(timeout))


@mcp.tool("element_wait_gone", tags={"element:wait"})
async def element_wait_gone(serial: str, xpath: str, timeout: float | None = None) -> bool:
    """
    wait until element gone

    Args:
        serial (str): Android device serialno
        xpath (str): element xpath
        timeout (Optional float): seconds wait element show up

    Returns:
        bool: True if gone else False
    """
    async with get_device(serial) as device:
        return await to_thread.run_sync(lambda: device.xpath(xpath).wait_gone(timeout))


@mcp.tool("element_click", tags={"element:interact"})
async def element_click(serial: str, xpath: str, timeout: float | None = None) -> bool:
    """
    find element and perform click

    Args:
        serial (str): Android device serialno
        xpath (str): element xpath
        timeout (Optional float): seconds wait element show up

    Returns:
        bool: True if click success else False
    """
    async with get_device(serial) as device:
        return await to_thread.run_sync(lambda: device.xpath(xpath).click_exists(timeout))


@mcp.tool("element_click_nowait", tags={"element:interact"})
async def element_click_nowait(serial: str, xpath: str):
    """
    find element and perform click

    Args:
        serial (str): Android device serialno
        xpath (str): element xpath
    """
    async with get_device(serial) as device:
        return await to_thread.run_sync(lambda: device.xpath(xpath).click_nowait())


@mcp.tool("element_click_until_gone", tags={"element:interact"})
async def element_click_until_gone(serial: str, xpath: str, maxretry=10, interval=1.0) -> bool:
    """
    find element and click until element is gone

    Args:
        serial (str): Android device serialno
        xpath (str): element xpath
        maxretry (int): max click times
        interval (float): sleep time between clicks

    Return:
        bool: if element is gone
    """
    async with get_device(serial) as device:
        return await to_thread.run_sync(lambda: device.xpath(xpath).click_gone(maxretry, interval))


@mcp.tool("element_long_click", tags={"element:interact"})
async def element_long_click(serial: str, xpath: str):
    """
    find element and perform long click

    Args:
        serial (str): Android device serialno
        xpath (str): element xpath
    """
    async with get_device(serial) as device:
        return await to_thread.run_sync(lambda: device.xpath(xpath).long_click())


@mcp.tool("element_screenshot", tags={"element:capture"})
async def element_screenshot(serial: str, xpath: str) -> dict[str, Any]:
    """
    find element and take screenshot

    Args:
        serial (str): Android device serialno
        xpath (str): element xpath

    Returns:
        dict[str,Any]: Screenshot image JPEG data with the following keys:
            - image (str): Base64 encoded image data in data URL format (data:image/jpeg;base64,...)
            - size (tuple[int,int]): Image dimensions as (width, height)
    """
    async with get_device(serial) as device:
        im = await to_thread.run_sync(lambda: device.xpath(xpath).screenshot())
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


@mcp.tool("element_get_text", tags={"element:query"})
async def element_get_text(serial: str, xpath: str) -> str | None:
    """
    find and get element text

    Args:
        serial (str): Android device serialno
        xpath (str): element xpath

    Returns:
        str: string of node text
        None: if element has no text attribute
    """
    async with get_device(serial) as device:
        return await to_thread.run_sync(lambda: device.xpath(xpath).get_text())


@mcp.tool("element_set_text", tags={"element:modify"})
async def element_set_text(serial: str, xpath: str, text: str) -> None:
    """
    find and set element text

    Args:
        serial (str): Android device serialno
        xpath (str): element xpath
        text (str): string of node text
    """
    async with get_device(serial) as device:
        return await to_thread.run_sync(lambda: device.xpath(xpath).set_text(text))


@mcp.tool("element_bounds", tags={"element:query"})
async def element_bounds(serial: str, xpath: str) -> tuple[int, int, int, int]:
    """
    find an element and get bounds

    Args:
        serial (str): Android device serialno
        xpath (str): element xpath

    Returns:
        tuple[int]: tuple of (left, top, right, bottom)
    """
    async with get_device(serial) as device:
        return await to_thread.run_sync(lambda: device.xpath(xpath).bounds())


@mcp.tool("element_swipe", tags={"element:gesture"})
async def element_swipe(serial: str, xpath: str, direction: str, scale: float = 0.6):
    """
    find an element and swipe

    Args:
        serial (str): Android device serialno
        xpath (str): element xpath
        direction: one of ["left", "right", "up", "down"]
        scale: percent of swipe, range (0, 1.0)
    """
    async with get_device(serial) as device:
        return await to_thread.run_sync(lambda: device.xpath(xpath).swipe(direction, scale))


@mcp.tool("element_scroll", tags={"element:gesture"})
async def element_scroll(serial: str, xpath: str, direction: str = "forward") -> bool:
    """
    find an element and scroll

    Args:
        serial (str): Android device serialno
        xpath (str): element xpath
        direction (str): scroll direction, one of ["forward", "backward"]

    Returns:
        bool: if can be scroll again
    """
    async with get_device(serial) as device:
        return await to_thread.run_sync(lambda: device.xpath(xpath).swipe(direction))


@mcp.tool("element_scroll_to", tags={"element:gesture"})
async def element_scroll_to(serial: str, xpath: str, direction: str = "forward", max_swipes: int = 10):
    """
    find an element and scroll to

    Args:
        serial (str): Android device serialno
        xpath (str): element xpath
        direction (str): scroll direction, one of ["forward", "backward"]
        max_swipes (int): max swipe times

    Returns:
        bool: if can be scroll again
    """
    async with get_device(serial) as device:
        return await to_thread.run_sync(lambda: device.xpath(xpath).scroll_to(direction, max_swipes))
