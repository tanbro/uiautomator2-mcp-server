"""
Unit tests for clipboard tools.
"""

from __future__ import annotations

import pytest

from u2mcp.tools.clipboard import read_clipboard, write_clipboard


@pytest.mark.asyncio
@pytest.mark.unit
async def test_read_clipboard(mock_u2_device) -> None:
    """Test read_clipboard executes without error."""
    await read_clipboard("emulator-5554")


@pytest.mark.asyncio
@pytest.mark.unit
async def test_write_clipboard(mock_u2_device) -> None:
    """Test write_clipboard executes without error."""
    await write_clipboard("emulator-5554", "Test text")
