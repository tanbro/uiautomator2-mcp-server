"""
Unit tests for element interaction tools.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from u2mcp.tools.element import (
    activity_wait,
    element_bounds,
    element_click,
    element_click_nowait,
    element_click_until_gone,
    element_get_text,
    element_long_click,
    element_screenshot,
    element_scroll,
    element_scroll_to,
    element_set_text,
    element_swipe,
    element_wait,
    element_wait_gone,
)


@pytest.mark.asyncio
@pytest.mark.unit
async def test_activity_wait(mock_u2_device: MagicMock) -> None:
    """Test activity_wait executes without error."""
    await activity_wait.fn("emulator-5554", ".MainActivity")


@pytest.mark.asyncio
@pytest.mark.unit
async def test_element_wait(mock_u2_device: MagicMock) -> None:
    """Test element_wait executes without error."""
    await element_wait.fn("emulator-5554", "//node[@text='Hello']")


@pytest.mark.asyncio
@pytest.mark.unit
async def test_element_wait_gone(mock_u2_device: MagicMock) -> None:
    """Test element_wait_gone executes without error."""
    await element_wait_gone.fn("emulator-5554", "//node[@text='Loading']")


@pytest.mark.asyncio
@pytest.mark.unit
async def test_element_click(mock_u2_device: MagicMock) -> None:
    """Test element_click executes without error."""
    await element_click.fn("emulator-5554", "//button[@text='Submit']")


@pytest.mark.asyncio
@pytest.mark.unit
async def test_element_click_nowait(mock_u2_device: MagicMock) -> None:
    """Test element_click_nowait executes without error."""
    await element_click_nowait.fn("emulator-5554", "//button[@text='Submit']")


@pytest.mark.asyncio
@pytest.mark.unit
async def test_element_click_until_gone(mock_u2_device: MagicMock) -> None:
    """Test element_click_until_gone executes without error."""
    await element_click_until_gone.fn("emulator-5554", "//node[@text='Close']")


@pytest.mark.asyncio
@pytest.mark.unit
async def test_element_long_click(mock_u2_device: MagicMock) -> None:
    """Test element_long_click executes without error."""
    await element_long_click.fn("emulator-5554", "//node[@text='Item']")


@pytest.mark.asyncio
@pytest.mark.unit
async def test_element_screenshot(mock_u2_device: MagicMock) -> None:
    """Test element_screenshot executes without error."""
    await element_screenshot.fn("emulator-5554", "//node[@resource-id='screenshot']")


@pytest.mark.asyncio
@pytest.mark.unit
async def test_element_get_text(mock_u2_device: MagicMock) -> None:
    """Test element_get_text executes without error."""
    await element_get_text.fn("emulator-5554", "//node[@text='Hello']")


@pytest.mark.asyncio
@pytest.mark.unit
async def test_element_set_text(mock_u2_device: MagicMock) -> None:
    """Test element_set_text executes without error."""
    await element_set_text.fn("emulator-5554", "//node[@resource-id='input']", "New text")


@pytest.mark.asyncio
@pytest.mark.unit
async def test_element_bounds(mock_u2_device: MagicMock) -> None:
    """Test element_bounds executes without error."""
    await element_bounds.fn("emulator-5554", "//node[@resource-id='button']")


@pytest.mark.asyncio
@pytest.mark.unit
async def test_element_swipe(mock_u2_device: MagicMock) -> None:
    """Test element_swipe executes without error."""
    await element_swipe.fn("emulator-5554", "//node[@scrollable='true']", "left")


@pytest.mark.asyncio
@pytest.mark.unit
async def test_element_scroll(mock_u2_device: MagicMock) -> None:
    """Test element_scroll executes without error."""
    await element_scroll.fn("emulator-5554", "//node[@scrollable='true']", "forward")


@pytest.mark.asyncio
@pytest.mark.unit
async def test_element_scroll_to(mock_u2_device: MagicMock) -> None:
    """Test element_scroll_to executes without error."""
    await element_scroll_to.fn("emulator-5554", "//node[@text='Target']")
