"""
Unit tests for action tools (click, swipe, drag, etc.).
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from u2mcp.tools.action import (
    clear_text,
    click,
    double_click,
    drag,
    hide_keyboard,
    long_click,
    press_key,
    screen_off,
    screen_on,
    send_text,
    swipe,
)


@pytest.mark.asyncio
@pytest.mark.unit
async def test_click(mock_u2_device: MagicMock) -> None:
    """Test click executes without error."""
    await click.fn("emulator-5554", 500, 1000)
    # If we get here without exception, the test passes


@pytest.mark.asyncio
@pytest.mark.unit
async def test_long_click(mock_u2_device: MagicMock) -> None:
    """Test long_click executes without error."""
    await long_click.fn("emulator-5554", 500, 1000)


@pytest.mark.asyncio
@pytest.mark.unit
async def test_double_click(mock_u2_device: MagicMock) -> None:
    """Test double_click executes without error."""
    await double_click.fn("emulator-5554", 500, 1000)


@pytest.mark.asyncio
@pytest.mark.unit
async def test_swipe(mock_u2_device: MagicMock) -> None:
    """Test swipe executes without error."""
    await swipe.fn("emulator-5554", 100, 200, 300, 400)


@pytest.mark.asyncio
@pytest.mark.unit
async def test_drag(mock_u2_device: MagicMock) -> None:
    """Test drag executes without error."""
    await drag.fn("emulator-5554", 100, 200, 300, 400)


@pytest.mark.asyncio
@pytest.mark.unit
async def test_press_key(mock_u2_device: MagicMock) -> None:
    """Test press_key executes without error."""
    await press_key.fn("emulator-5554", "home")


@pytest.mark.asyncio
@pytest.mark.unit
async def test_send_text(mock_u2_device: MagicMock) -> None:
    """Test send_text executes without error."""
    await send_text.fn("emulator-5554", "Hello World")


@pytest.mark.asyncio
@pytest.mark.unit
async def test_clear_text(mock_u2_device: MagicMock) -> None:
    """Test clear_text executes without error."""
    await clear_text.fn("emulator-5554")


@pytest.mark.asyncio
@pytest.mark.unit
async def test_screen_on(mock_u2_device: MagicMock) -> None:
    """Test screen_on executes without error."""
    await screen_on.fn("emulator-5554")


@pytest.mark.asyncio
@pytest.mark.unit
async def test_screen_off(mock_u2_device: MagicMock) -> None:
    """Test screen_off executes without error."""
    await screen_off.fn("emulator-5554")


@pytest.mark.asyncio
@pytest.mark.unit
async def test_hide_keyboard(mock_u2_device: MagicMock) -> None:
    """Test hide_keyboard executes without error."""
    await hide_keyboard.fn("emulator-5554")
