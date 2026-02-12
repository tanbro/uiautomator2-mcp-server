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
    "select_click",
    "select_long_press",
    "select_wait_appear",
    "select_wait_gone",
    "select_get_text",
    "select_get_bounds",
    "select_set_text",
    "select_swipe",
    "select_scroll",
    "select_screenshot",
    "select_save_screenshot",
)


def _build_selector(
    text: str = "",
    resource_id: str = "",
    class_name: str = "",
    description: str = "",
) -> dict:
    """Build selector dict from keyword arguments.

    Args:
        text: Element text content to match.
        resource_id: Element resource ID.
        class_name: Element class name.
        description: Element content description.

    Returns:
        dict: Selector dictionary for uiautomator2.
    """
    selector = {}
    if text:
        selector["text"] = text
    if resource_id:
        selector["resourceId"] = resource_id
    if class_name:
        selector["className"] = class_name
    if description:
        selector["description"] = description
    return selector


@mcp.tool("select_click", tags={"selector:interact"})
async def select_click(
    serial: str,
    text: str = "",
    resource_id: str = "",
    class_name: str = "",
    description: str = "",
) -> bool:
    """Click on an element using selector-based location.

    Args:
        serial (str): Android device serial number.
        text (str): Element text content to match.
        resource_id (str): Element resource ID.
        class_name (str): Element class name.
        description (str): Element content description.

    Returns:
        bool: True if click successful, False otherwise.
    """
    selector = _build_selector(text=text, resource_id=resource_id, class_name=class_name, description=description)

    async with get_device(serial) as device:
        return await to_thread.run_sync(lambda: device(**selector).click_exists(timeout=10.0))


@mcp.tool("select_long_press", tags={"selector:interact"})
async def select_long_press(
    serial: str,
    duration: float,
    text: str = "",
    resource_id: str = "",
    class_name: str = "",
    description: str = "",
) -> bool:
    """Long press on an element using selector-based location.

    Args:
        serial (str): Android device serial number.
        duration (float): Duration of long press in seconds.
        text (str): Element text content to match.
        resource_id (str): Element resource ID.
        class_name (str): Element class name.
        description (str): Element content description.

    Returns:
        bool: True if long press successful, False otherwise.
    """
    selector = _build_selector(text=text, resource_id=resource_id, class_name=class_name, description=description)

    async with get_device(serial) as device:
        return await to_thread.run_sync(lambda: device(**selector).long_click(duration))


@mcp.tool("select_wait_appear", tags={"selector:wait"})
async def select_wait_appear(
    serial: str,
    timeout: float,
    text: str = "",
    resource_id: str = "",
    class_name: str = "",
    description: str = "",
) -> bool:
    """Wait for an element to appear using selector-based location.

    Args:
        serial (str): Android device serial number.
        timeout (float): Maximum wait time in seconds.
        text (str): Element text content to match.
        resource_id (str): Element resource ID.
        class_name (str): Element class name.
        description (str): Element content description.

    Returns:
        bool: True if element appeared, False if timeout.
    """
    selector = _build_selector(text=text, resource_id=resource_id, class_name=class_name, description=description)

    async with get_device(serial) as device:
        return await to_thread.run_sync(
            lambda: device(**selector).wait(timeout)  # type: ignore[arg-type]
        )


@mcp.tool("select_wait_gone", tags={"selector:wait"})
async def select_wait_gone(
    serial: str,
    timeout: float,
    text: str = "",
    resource_id: str = "",
    class_name: str = "",
    description: str = "",
) -> bool:
    """Wait for an element to disappear using selector-based location.

    Args:
        serial (str): Android device serial number.
        timeout (float): Maximum wait time in seconds.
        text (str): Element text content to match.
        resource_id (str): Element resource ID.
        class_name (str): Element class name.
        description (str): Element content description.

    Returns:
        bool: True if element gone, False if still present after timeout.
    """
    selector = _build_selector(text=text, resource_id=resource_id, class_name=class_name, description=description)

    async with get_device(serial) as device:
        return await to_thread.run_sync(lambda: device(**selector).wait_gone(timeout))


@mcp.tool("select_get_text", tags={"selector:query"})
async def select_get_text(
    serial: str,
    text: str = "",
    resource_id: str = "",
    class_name: str = "",
    description: str = "",
) -> str:
    """Get element text content using selector-based location.

    Args:
        serial (str): Android device serial number.
        text (str): Element text content to match.
        resource_id (str): Element resource ID.
        class_name (str): Element class name.
        description (str): Element content description.

    Returns:
        str: Element text content, empty string if not found.
    """
    selector = _build_selector(text=text, resource_id=resource_id, class_name=class_name, description=description)

    async with get_device(serial) as device:
        elem = device(**selector)
        if await to_thread.run_sync(elem.wait, True, 1.0):
            result = elem.info.get("text")
            if result:
                return result
    return ""


@mcp.tool("select_get_bounds", tags={"selector:query"})
async def select_get_bounds(
    serial: str,
    text: str = "",
    resource_id: str = "",
    class_name: str = "",
    description: str = "",
) -> tuple[int, int, int, int]:
    """Get element bounding box using selector-based location.

    Args:
        serial (str): Android device serial number.
        text (str): Element text content to match.
        resource_id (str): Element resource ID.
        class_name (str): Element class name.
        description (str): Element content description.

    Returns:
        tuple[int, int, int, int]: Element bounds as (left, top, right, bottom).
            Returns (0, 0, 0, 0) if element not found.
    """
    selector = _build_selector(text=text, resource_id=resource_id, class_name=class_name, description=description)

    async with get_device(serial) as device:
        elem = device(**selector)
        if await to_thread.run_sync(elem.wait, True, 1.0):
            bounds = elem.info.get("bounds")
            if bounds:
                return (bounds["left"], bounds["top"], bounds["right"], bounds["bottom"])
    return (0, 0, 0, 0)


@mcp.tool("select_set_text", tags={"selector:modify"})
async def select_set_text(
    serial: str,
    text: str,
    text_match: str = "",
    resource_id: str = "",
    class_name: str = "",
    description: str = "",
):
    """Set text on an element using selector-based location.

    Args:
        serial (str): Android device serial number.
        text (str): Text content to set.
        text_match (str): Element text content to match for selector.
        resource_id (str): Element resource ID.
        class_name (str): Element class name.
        description (str): Element content description.
    """
    selector = _build_selector(text=text_match, resource_id=resource_id, class_name=class_name, description=description)

    async with get_device(serial) as device:
        await to_thread.run_sync(lambda: device(**selector).set_text(text))


@mcp.tool("select_swipe", tags={"selector:gesture"})
async def select_swipe(
    serial: str,
    direction: str,
    text: str = "",
    resource_id: str = "",
    class_name: str = "",
    description: str = "",
    scale: float = 0.6,
):
    """Swipe within an element using selector-based location.

    Args:
        serial (str): Android device serial number.
        direction (str): Swipe direction, one of left, right, up, down.
        text (str): Element text content to match.
        resource_id (str): Element resource ID.
        class_name (str): Element class name.
        description (str): Element content description.
        scale (float): Percentage of swipe distance, range (0, 1.0).
    """
    selector = _build_selector(text=text, resource_id=resource_id, class_name=class_name, description=description)

    async with get_device(serial) as device:
        await to_thread.run_sync(lambda: device(**selector).swipe(direction, scale))


@mcp.tool("select_scroll", tags={"selector:gesture"})
async def select_scroll(
    serial: str,
    direction: str,
    text: str = "",
    resource_id: str = "",
    class_name: str = "",
    description: str = "",
) -> bool:
    """Scroll within a scrollable element using selector-based location.

    Args:
        serial (str): Android device serial number.
        direction (str): Scroll direction, one of forward, backward, left, right, up, down.
        text (str): Element text content to match.
        resource_id (str): Element resource ID.
        class_name (str): Element class name.
        description (str): Element content description.

    Returns:
        bool: True if can scroll further, False otherwise.
    """
    selector = _build_selector(text=text, resource_id=resource_id, class_name=class_name, description=description)

    async with get_device(serial) as device:
        return await to_thread.run_sync(lambda: device(**selector).scroll(direction))


@mcp.tool("select_screenshot", tags={"selector:capture"})
async def select_screenshot(
    serial: str,
    format: str,
    text: str = "",
    resource_id: str = "",
    class_name: str = "",
    description: str = "",
) -> tuple[str, int, int]:
    """Take a screenshot of an element using selector-based location.

    Args:
        serial (str): Android device serial number.
        format (str): Image format, jpeg or png.
        text (str): Element text content to match.
        resource_id (str): Element resource ID.
        class_name (str): Element class name.
        description (str): Element content description.

    Returns:
        tuple[str, int, int]: Base64 encoded image data URL, image height, image width.
    """
    selector = _build_selector(text=text, resource_id=resource_id, class_name=class_name, description=description)

    async with get_device(serial) as device:
        im = await to_thread.run_sync(lambda: device(**selector).screenshot())

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


@mcp.tool("select_save_screenshot", tags={"selector:capture"})
async def select_save_screenshot(
    serial: str,
    file: str,
    text: str = "",
    resource_id: str = "",
    class_name: str = "",
    description: str = "",
) -> str:
    """Save a screenshot of an element to file using selector-based location.

    Args:
        serial (str): Android device serial number.
        file (str): File path to save the screenshot. Format determined by extension.
        text (str): Element text content to match.
        resource_id (str): Element resource ID.
        class_name (str): Element class name.
        description (str): Element content description.

    Returns:
        str: Absolute path to the saved screenshot file.
    """
    selector = _build_selector(text=text, resource_id=resource_id, class_name=class_name, description=description)

    async with get_device(serial) as device:
        im = await to_thread.run_sync(lambda: device(**selector).screenshot())

    if not isinstance(im, Image):
        raise RuntimeError("Invalid image")

    with closing(im):
        file_path = Path(file)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        im.save(file_path)

    return file_path.resolve().as_posix()
