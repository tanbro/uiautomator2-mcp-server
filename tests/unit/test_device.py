"""
Unit tests for device management tools.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from u2mcp.tools.device import (
    connect,
    device_list,
    disconnect,
    disconnect_all,
    info,
    window_size,
)


@pytest.mark.asyncio
@pytest.mark.unit
async def test_device_list(mock_adb: MagicMock) -> None:
    """Test device_list returns expected device information."""
    # Setup mock device
    mock_device = MagicMock()
    mock_device.info = {"serial": "emulator-5554", "model": "test_device"}
    mock_adb.device_list.return_value = [mock_device]

    # Execute using the underlying function
    result = await device_list.fn()

    # Verify
    assert len(result) == 1
    assert result[0]["serial"] == "emulator-5554"
    assert result[0]["model"] == "test_device"
    mock_adb.device_list.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.unit
async def test_device_list_empty(mock_adb: MagicMock) -> None:
    """Test device_list returns empty list when no devices connected."""
    mock_adb.device_list.return_value = []

    result = await device_list.fn()

    assert result == []
    mock_adb.device_list.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.unit
async def test_window_size(mock_u2_device: MagicMock) -> None:
    """Test window_size returns device screen dimensions."""
    # mock_u2_device is provided by autouse fixture
    result = await window_size.fn("emulator-5554")

    assert result == {"width": 1080, "height": 2400}


@pytest.mark.asyncio
@pytest.mark.unit
async def test_info(mock_u2_device: MagicMock) -> None:
    """Test info returns device information."""
    # mock_u2_device.info is already set to a dict in the fixture
    expected_info = mock_u2_device.info

    result = await info.fn("emulator-5554")

    assert result == expected_info


@pytest.mark.asyncio
@pytest.mark.unit
async def test_connect_success(mock_u2_device: MagicMock) -> None:
    """Test connect returns device information."""
    # connect function may return merged device_info and info
    result = await connect.fn("emulator-5554")

    # Should return a dictionary with device information
    assert isinstance(result, dict)
    # Should contain expected keys from device_info and info
    assert "serial" in result
    assert "productName" in result


@pytest.mark.asyncio
@pytest.mark.unit
async def test_disconnect(mock_u2_device: MagicMock) -> None:
    """Test disconnect executes without error."""
    # disconnect may return None or a message
    result = await disconnect.fn("emulator-5554")
    # Just ensure no exception raised
    assert result is None or isinstance(result, str)


@pytest.mark.asyncio
@pytest.mark.unit
async def test_disconnect_all(mock_u2_device: MagicMock) -> None:
    """Test disconnect_all executes without error."""
    result = await disconnect_all.fn()
    # Just ensure no exception raised
    assert result is None or isinstance(result, str)
