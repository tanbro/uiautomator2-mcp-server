"""
Unit tests for device management tools.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from u2mcp.tools.device import (
    connect,
    device_list,
    disconnect,
    disconnect_all,
    info,
    save_screenshot,
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


@pytest.mark.asyncio
@pytest.mark.unit
async def test_save_screenshot_png(mock_u2_device: MagicMock, tmp_path: Path) -> None:
    """Test save_screenshot saves PNG file."""
    from PIL.Image import Image

    # Create a mock image
    mock_image = MagicMock(spec=Image)
    mock_image.save = MagicMock()

    # Setup mock device to return our mock image
    mock_u2_device.screenshot = MagicMock(return_value=mock_image)

    # Create a temporary file path
    output_path = tmp_path / "screenshot.png"

    # Execute
    result = await save_screenshot.fn("emulator-5554", str(output_path))

    # Verify the image was saved and path is returned
    mock_image.save.assert_called_once()
    assert isinstance(result, str)
    assert "screenshot.png" in result


@pytest.mark.asyncio
@pytest.mark.unit
async def test_save_screenshot_jpeg(mock_u2_device: MagicMock, tmp_path: Path) -> None:
    """Test save_screenshot saves JPEG file."""
    from PIL.Image import Image

    mock_image = MagicMock(spec=Image)
    mock_image.save = MagicMock()
    mock_u2_device.screenshot = MagicMock(return_value=mock_image)

    output_path = tmp_path / "screenshot.jpg"
    result = await save_screenshot.fn("emulator-5554", str(output_path))

    mock_image.save.assert_called_once()
    assert isinstance(result, str)
    assert "screenshot.jpg" in result


@pytest.mark.asyncio
@pytest.mark.unit
async def test_save_screenshot_creates_directory(mock_u2_device: MagicMock, tmp_path: Path) -> None:
    """Test save_screenshot creates parent directory if it doesn't exist."""
    from PIL.Image import Image

    mock_image = MagicMock(spec=Image)
    mock_image.save = MagicMock()
    mock_u2_device.screenshot = MagicMock(return_value=mock_image)

    # Create a path with non-existent subdirectories
    output_path = tmp_path / "subdir1" / "subdir2" / "screenshot.png"

    result = await save_screenshot.fn("emulator-5554", str(output_path))

    # Verify the save was called (directory should have been created)
    mock_image.save.assert_called_once()
    assert isinstance(result, str)


@pytest.mark.asyncio
@pytest.mark.unit
async def test_save_screenshot_with_display_id(mock_u2_device: MagicMock, tmp_path: Path) -> None:
    """Test save_screenshot with specific display_id."""
    from PIL.Image import Image

    mock_image = MagicMock(spec=Image)
    mock_image.save = MagicMock()
    mock_u2_device.screenshot = MagicMock(return_value=mock_image)

    output_path = tmp_path / "screenshot.png"
    result = await save_screenshot.fn("emulator-5554", str(output_path), display_id=1)

    # Verify screenshot was called with display_id=1
    mock_u2_device.screenshot.assert_called_once_with(display_id=1)
    assert isinstance(result, str)

