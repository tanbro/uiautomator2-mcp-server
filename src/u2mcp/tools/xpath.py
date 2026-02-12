from __future__ import annotations

from base64 import b64encode
from contextlib import closing
from io import BytesIO
from pathlib import Path

from anyio import to_thread
from PIL.Image import Image

from ..mcp import mcp
from .device import get_device

__all__ = (
    "xpath_wait_appear",
    "xpath_wait_gone",
    "xpath_exists",
    "xpath_click",
    "xpath_click_nowait",
    "xpath_long_press",
    "xpath_screenshot",
    "xpath_save_screenshot",
    "xpath_get_text",
    "xpath_set_text",
    "xpath_get_bounds",
    "xpath_get_info",
    "xpath_get_attrib",
    "xpath_swipe",
    "xpath_scroll",
    "xpath_scroll_to",
)


@mcp.tool("xpath_wait_appear", tags={"xpath:wait"})
async def xpath_wait_appear(serial: str, xpath: str, timeout: float) -> bool:
    """Wait until element is found using XPath.

    Args:
        serial (str): Android device serial number.
        xpath (str): Element XPath expression.
        timeout (float): Maximum wait time in seconds.

    Returns:
        bool: True if element found, False if timeout.
    """
    async with get_device(serial) as device:
        return await to_thread.run_sync(lambda: device.xpath(xpath).wait(timeout))


@mcp.tool("xpath_wait_gone", tags={"xpath:wait"})
async def xpath_wait_gone(serial: str, xpath: str, timeout: float) -> bool:
    """Wait until element disappears using XPath.

    Args:
        serial (str): Android device serial number.
        xpath (str): Element XPath expression.
        timeout (float): Maximum wait time in seconds.

    Returns:
        bool: True if element gone, False if still present after timeout.
    """
    async with get_device(serial) as device:
        return await to_thread.run_sync(lambda: device.xpath(xpath).wait_gone(timeout))


@mcp.tool("xpath_click", tags={"xpath:interact"})
async def xpath_click(serial: str, xpath: str, timeout: float) -> bool:
    """Find element by XPath and perform click.

    Args:
        serial (str): Android device serial number.
        xpath (str): Element XPath expression.
        timeout (float): Maximum wait time in seconds.

    Returns:
        bool: True if click successful, False otherwise.
    """
    async with get_device(serial) as device:
        return await to_thread.run_sync(lambda: device.xpath(xpath).click_exists(timeout))


@mcp.tool("xpath_click_nowait", tags={"xpath:interact"})
async def xpath_click_nowait(serial: str, xpath: str):
    """Find element by XPath and click immediately without waiting.

    Args:
        serial (str): Android device serial number.
        xpath (str): Element XPath expression.
    """
    async with get_device(serial) as device:
        await to_thread.run_sync(lambda: device.xpath(xpath).click_nowait())


@mcp.tool("xpath_long_press", tags={"xpath:interact"})
async def xpath_long_press(serial: str, xpath: str):
    """Find element by XPath and perform long press.

    Args:
        serial (str): Android device serial number.
        xpath (str): Element XPath expression.
    """
    async with get_device(serial) as device:
        await to_thread.run_sync(lambda: device.xpath(xpath).long_click())


@mcp.tool("xpath_screenshot", tags={"xpath:capture"})
async def xpath_screenshot(serial: str, xpath: str, format: str) -> tuple[str, int, int]:
    """Find element by XPath and take screenshot.

    Args:
        serial (str): Android device serial number.
        xpath (str): Element XPath expression.
        format (str): Image format, jpeg or png.

    Returns:
        tuple[str, int, int]: Base64 encoded image data URL, image height, image width.
    """
    async with get_device(serial) as device:
        im = await to_thread.run_sync(lambda: device.xpath(xpath).screenshot())

    if not isinstance(im, Image):
        raise RuntimeError("Invalid image")

    with closing(im):
        with BytesIO() as fp:
            im.save(fp, format)
            im_data = fp.getvalue()

        return (
            f"data:image/{format};base64," + b64encode(im_data).decode(),
            im.height,
            im.width,
        )


@mcp.tool("xpath_save_screenshot", tags={"xpath:capture"})
async def xpath_save_screenshot(serial: str, xpath: str, file: str) -> str:
    """Find element by XPath and save screenshot to file.

    Args:
        serial (str): Android device serial number.
        xpath (str): Element XPath expression.
        file (str): File path to save the screenshot. Format determined by extension.

    Returns:
        str: Absolute path to the saved screenshot file.
    """
    async with get_device(serial) as device:
        im = await to_thread.run_sync(lambda: device.xpath(xpath).screenshot())

    if not isinstance(im, Image):
        raise RuntimeError("Invalid image")

    with closing(im):
        file_path = Path(file)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        im.save(file_path)

    return file_path.resolve().as_posix()


@mcp.tool("xpath_get_text", tags={"xpath:query"})
async def xpath_get_text(serial: str, xpath: str) -> str:
    """Find element by XPath and get its text content.

    Args:
        serial (str): Android device serial number.
        xpath (str): Element XPath expression.

    Returns:
        str: Element text content, empty string if element has no text.
    """
    async with get_device(serial) as device:
        result = await to_thread.run_sync(lambda: device.xpath(xpath).get_text())
        return result if result else ""


@mcp.tool("xpath_set_text", tags={"xpath:modify"})
async def xpath_set_text(serial: str, xpath: str, text: str):
    """Find element by XPath and set its text content.

    Args:
        serial (str): Android device serial number.
        xpath (str): Element XPath expression.
        text (str): Text content to set.
    """
    async with get_device(serial) as device:
        await to_thread.run_sync(lambda: device.xpath(xpath).set_text(text))


@mcp.tool("xpath_get_bounds", tags={"xpath:query"})
async def xpath_get_bounds(serial: str, xpath: str) -> tuple[int, int, int, int]:
    """Find element by XPath and get its bounding box.

    Args:
        serial (str): Android device serial number.
        xpath (str): Element XPath expression.

    Returns:
        tuple[int, int, int, int]: Element bounds as (left, top, right, bottom).
    """
    async with get_device(serial) as device:
        return await to_thread.run_sync(lambda: device.xpath(xpath).bounds)


@mcp.tool("xpath_exists", tags={"xpath:query"})
async def xpath_exists(serial: str, xpath: str) -> bool:
    """Check if element exists by XPath without waiting.

    Args:
        serial (str): Android device serial number.
        xpath (str): Element XPath expression.

    Returns:
        bool: True if element exists, False otherwise.
    """
    async with get_device(serial) as device:
        return await to_thread.run_sync(lambda: device.xpath(xpath).exists)


@mcp.tool("xpath_get_info", tags={"xpath:query"})
async def xpath_get_info(serial: str, xpath: str) -> dict[str, object]:
    """Find element by XPath and get its complete information.

    Args:
        serial (str): Android device serial number.
        xpath (str): Element XPath expression.

    Returns:
        dict[str, object]: Element information including text, bounds, className, clickable, etc.
    """
    async with get_device(serial) as device:
        element = await to_thread.run_sync(lambda: device.xpath(xpath).get())
        return element.info


@mcp.tool("xpath_get_attrib", tags={"xpath:query"})
async def xpath_get_attrib(serial: str, xpath: str, key: str) -> str:
    """Find element by XPath and get a specific attribute value.

    Args:
        serial (str): Android device serial number.
        xpath (str): Element XPath expression.
        key (str): Attribute name to retrieve.

    Returns:
        str: Attribute value, empty string if attribute not found.
    """
    async with get_device(serial) as device:
        element = await to_thread.run_sync(lambda: device.xpath(xpath).get())
        return element.attrib.get(key, "")


@mcp.tool("xpath_swipe", tags={"xpath:gesture"})
async def xpath_swipe(serial: str, xpath: str, direction: str, scale: float = 0.6):
    """Find element by XPath and swipe within it.

    Args:
        serial (str): Android device serial number.
        xpath (str): Element XPath expression.
        direction (str): Swipe direction, one of left, right, up, down.
        scale (float): Percentage of swipe distance, range (0, 1.0).
    """
    async with get_device(serial) as device:
        await to_thread.run_sync(lambda: device.xpath(xpath).swipe(direction, scale))


@mcp.tool("xpath_scroll", tags={"xpath:gesture"})
async def xpath_scroll(serial: str, xpath: str, direction: str) -> bool:
    """Find element by XPath and scroll within it.

    Args:
        serial (str): Android device serial number.
        xpath (str): Element XPath expression.
        direction (str): Scroll direction, one of forward or backward.

    Returns:
        bool: True if can scroll further, False otherwise.
    """
    async with get_device(serial) as device:
        return await to_thread.run_sync(lambda: device.xpath(xpath).scroll(direction))


@mcp.tool("xpath_scroll_to", tags={"xpath:gesture"})
async def xpath_scroll_to(serial: str, xpath: str, direction: str, max_swipes: int) -> bool:
    """Scroll the entire screen to find an element by XPath.

    Args:
        serial (str): Android device serial number.
        xpath (str): Target element XPath expression to scroll to.
        direction (str): Scroll direction, one of forward or backward.
        max_swipes (int): Maximum swipe attempts.

    Returns:
        bool: True if element found, False otherwise.
    """
    async with get_device(serial) as device:
        result = await to_thread.run_sync(lambda: device.xpath.scroll_to(xpath, direction, max_swipes))
        return result is not None
