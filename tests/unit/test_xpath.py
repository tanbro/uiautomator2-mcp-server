"""Unit tests for XPath-based element interaction tools."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from u2mcp.tools.xpath import (
    xpath_click,
    xpath_click_nowait,
    xpath_exists,
    xpath_get_attrib,
    xpath_get_bounds,
    xpath_get_info,
    xpath_get_text,
    xpath_long_press,
    xpath_save_screenshot,
    xpath_screenshot,
    xpath_scroll,
    xpath_scroll_to,
    xpath_set_text,
    xpath_swipe,
    xpath_wait_appear,
    xpath_wait_gone,
)


@pytest.mark.asyncio
@pytest.mark.unit
async def test_xpath_wait_appear(mock_u2_device: MagicMock) -> None:
    """Test xpath_wait_appear executes without error."""
    await xpath_wait_appear("emulator-5554", "//node[@text='Hello']", 10.0)


@pytest.mark.asyncio
@pytest.mark.unit
async def test_xpath_wait_gone(mock_u2_device: MagicMock) -> None:
    """Test xpath_wait_gone executes without error."""
    await xpath_wait_gone("emulator-5554", "//node[@text='Loading']", 10.0)


@pytest.mark.asyncio
@pytest.mark.unit
async def test_xpath_exists(mock_u2_device: MagicMock) -> None:
    """Test xpath_exists executes without error."""
    result = await xpath_exists("emulator-5554", "//node[@text='Hello']")
    assert result is True


@pytest.mark.asyncio
@pytest.mark.unit
async def test_xpath_click(mock_u2_device: MagicMock) -> None:
    """Test xpath_click executes without error."""
    result = await xpath_click("emulator-5554", "//button[@text='Submit']", 10.0)
    assert result is True


@pytest.mark.asyncio
@pytest.mark.unit
async def test_xpath_click_nowait(mock_u2_device: MagicMock) -> None:
    """Test xpath_click_nowait executes without error."""
    await xpath_click_nowait("emulator-5554", "//button[@text='Submit']")


@pytest.mark.asyncio
@pytest.mark.unit
async def test_xpath_long_press(mock_u2_device: MagicMock) -> None:
    """Test xpath_long_press executes without error."""
    await xpath_long_press("emulator-5554", "//node[@text='Item']")


@pytest.mark.asyncio
@pytest.mark.unit
async def test_xpath_screenshot(mock_u2_device: MagicMock) -> None:
    """Test xpath_screenshot returns base64 data URL."""
    data_url, height, width = await xpath_screenshot("emulator-5554", "//node[@resource-id='screenshot']", "jpeg")
    assert data_url.startswith("data:image/jpeg;base64,")
    assert height == 200
    assert width == 100


@pytest.mark.asyncio
@pytest.mark.unit
async def test_xpath_save_screenshot(mock_u2_device: MagicMock) -> None:
    """Test xpath_save_screenshot saves to file."""
    import tempfile

    with tempfile.NamedTemporaryFile(suffix=".png", delete=True) as tmp:
        result = await xpath_save_screenshot("emulator-5554", "//node[@resource-id='screenshot']", tmp.name)
        assert result.endswith(".png")


@pytest.mark.asyncio
@pytest.mark.unit
async def test_xpath_get_text(mock_u2_device: MagicMock) -> None:
    """Test xpath_get_text returns element text."""
    result = await xpath_get_text("emulator-5554", "//node[@text='Hello']")
    assert result == "Sample text"


@pytest.mark.asyncio
@pytest.mark.unit
async def test_xpath_get_text_empty(mock_u2_device: MagicMock) -> None:
    """Test xpath_get_text returns empty string when element has no text."""
    # Mock the xpath to return None
    mock_u2_device.xpath.return_value.get_text = MagicMock(return_value=None)
    result = await xpath_get_text("emulator-5554", "//node[@text='Empty']")
    assert result == ""


@pytest.mark.asyncio
@pytest.mark.unit
async def test_xpath_set_text(mock_u2_device: MagicMock) -> None:
    """Test xpath_set_text executes without error."""
    await xpath_set_text("emulator-5554", "//node[@resource-id='input']", "New text")


@pytest.mark.asyncio
@pytest.mark.unit
async def test_xpath_get_bounds(mock_u2_device: MagicMock) -> None:
    """Test xpath_get_bounds returns element bounds."""
    # The mock returns MagicMock, need to ensure bounds is properly mocked
    mock_u2_device.xpath.return_value.bounds = (100, 200, 300, 400)
    result = await xpath_get_bounds("emulator-5554", "//node[@resource-id='button']")
    assert result == (100, 200, 300, 400)


@pytest.mark.asyncio
@pytest.mark.unit
async def test_xpath_get_info(mock_u2_device: MagicMock) -> None:
    """Test xpath_get_info returns element info dict."""
    # Mock the xpath().get() to return an element with info
    mock_element = MagicMock()
    mock_element.info = {"text": "Sample", "bounds": "(100,200)(300,400)"}
    mock_u2_device.xpath.return_value.get = MagicMock(return_value=mock_element)

    result = await xpath_get_info("emulator-5554", "//node[@text='Sample']")
    assert result == {"text": "Sample", "bounds": "(100,200)(300,400)"}


@pytest.mark.asyncio
@pytest.mark.unit
async def test_xpath_get_attrib(mock_u2_device: MagicMock) -> None:
    """Test xpath_get_attrib returns specific attribute value."""
    # Mock the xpath().get() to return an element with attrib
    mock_element = MagicMock()
    mock_element.attrib = MagicMock()
    mock_element.attrib.get = MagicMock(return_value="attribute_value")
    mock_u2_device.xpath.return_value.get = MagicMock(return_value=mock_element)

    result = await xpath_get_attrib("emulator-5554", "//node[@text='Sample']", "text")
    assert result == "attribute_value"


@pytest.mark.asyncio
@pytest.mark.unit
async def test_xpath_get_attrib_not_found(mock_u2_device: MagicMock) -> None:
    """Test xpath_get_attrib returns empty string when attribute not found."""
    # Mock the xpath().get() to return an element with attrib that returns default value
    mock_element = MagicMock()
    mock_element.attrib = MagicMock()
    # When .get() is called with no matching key, return default empty string
    mock_element.attrib.get = MagicMock(return_value="")
    mock_u2_device.xpath.return_value.get = MagicMock(return_value=mock_element)

    result = await xpath_get_attrib("emulator-5554", "//node[@text='Sample']", "nonexistent")
    assert result == ""


@pytest.mark.asyncio
@pytest.mark.unit
async def test_xpath_swipe(mock_u2_device: MagicMock) -> None:
    """Test xpath_swipe executes without error."""
    await xpath_swipe("emulator-5554", "//node[@scrollable='true']", "left", 0.6)


@pytest.mark.asyncio
@pytest.mark.unit
async def test_xpath_swipe_default_scale(mock_u2_device: MagicMock) -> None:
    """Test xpath_swipe uses default scale of 0.6."""
    await xpath_swipe("emulator-5554", "//node[@scrollable='true']", "right")


@pytest.mark.asyncio
@pytest.mark.unit
async def test_xpath_scroll(mock_u2_device: MagicMock) -> None:
    """Test xpath_scroll executes without error."""
    result = await xpath_scroll("emulator-5554", "//node[@scrollable='true']", "forward")
    assert result is True


@pytest.mark.asyncio
@pytest.mark.unit
async def test_xpath_scroll_to(mock_u2_device: MagicMock) -> None:
    """Test xpath_scroll_to executes without error."""
    result = await xpath_scroll_to("emulator-5554", "//node[@text='Target']", "forward", 10)
    assert result is True
