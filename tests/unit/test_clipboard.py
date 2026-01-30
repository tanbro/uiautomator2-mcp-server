"""
Unit tests for clipboard tools.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from u2mcp.tools.clipboard import read_clipboard, write_clipboard


@pytest.mark.asyncio
@pytest.mark.unit
async def test_read_clipboard(mock_u2_device: MagicMock) -> None:
    """Test read_clipboard executes without error."""
    await read_clipboard.fn("emulator-5554")


@pytest.mark.asyncio
@pytest.mark.unit
async def test_write_clipboard(mock_u2_device: MagicMock) -> None:
    """Test write_clipboard executes without error."""
    await write_clipboard.fn("emulator-5554", "Test text")
