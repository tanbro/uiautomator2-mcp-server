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
    dump_hierarchy,
    info,
    save_dump_hierarchy,
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


@pytest.mark.asyncio
@pytest.mark.unit
async def test_dump_hierarchy_full(mock_u2_device: MagicMock) -> None:
    """Test dump_hierarchy returns full XML when no xpath provided."""
    sample_xml = """<?xml version='1.0' encoding='UTF-8'?>
<hierarchy>
    <node resource-id="button1" text="Click Me" clickable="true"/>
    <node resource-id="button2" text="Don't Click" clickable="false"/>
</hierarchy>"""
    mock_u2_device.dump_hierarchy = MagicMock(return_value=sample_xml)

    result = await dump_hierarchy.fn("emulator-5554")

    assert result == sample_xml
    mock_u2_device.dump_hierarchy.assert_called_once_with(compressed=False, pretty=False, max_depth=None)


@pytest.mark.asyncio
@pytest.mark.unit
async def test_dump_hierarchy_with_xpath_single_match(mock_u2_device: MagicMock) -> None:
    """Test dump_hierarchy filters by xpath when single match."""
    sample_xml = """<?xml version='1.0' encoding='UTF-8'?>
<hierarchy>
    <node resource-id="button1" text="Click Me" clickable="true"/>
    <node resource-id="button2" text="Don't Click" clickable="false"/>
</hierarchy>"""
    mock_u2_device.dump_hierarchy = MagicMock(return_value=sample_xml)

    result = await dump_hierarchy.fn("emulator-5554", xpath="//*[@clickable='true']")

    # Should return only the clickable button
    assert 'resource-id="button1"' in result
    assert 'text="Click Me"' in result
    assert 'clickable="true"' in result
    # Should not contain the non-clickable button
    assert 'resource-id="button2"' not in result


@pytest.mark.asyncio
@pytest.mark.unit
async def test_dump_hierarchy_with_xpath_multiple_matches(mock_u2_device: MagicMock) -> None:
    """Test dump_hierarchy returns XML separated by === when xpath matches multiple nodes."""
    sample_xml = """<?xml version='1.0' encoding='UTF-8'?>
<hierarchy>
    <node resource-id="button1" text="Button 1" clickable="true"/>
    <node resource-id="button2" text="Button 2" clickable="true"/>
    <node resource-id="text" text="Label" clickable="false"/>
</hierarchy>"""
    mock_u2_device.dump_hierarchy = MagicMock(return_value=sample_xml)

    result = await dump_hierarchy.fn("emulator-5554", xpath="//*[@clickable='true']")

    # Should return both clickable buttons separated by ===
    assert 'resource-id="button1"' in result
    assert 'resource-id="button2"' in result
    assert 'clickable="true"' in result
    # Check for === separator
    assert "\n===\n" in result
    # Should not contain the non-clickable element
    assert 'resource-id="text"' not in result


@pytest.mark.asyncio
@pytest.mark.unit
async def test_dump_hierarchy_with_xpath_no_match(mock_u2_device: MagicMock) -> None:
    """Test dump_hierarchy returns empty string when xpath matches nothing."""
    sample_xml = """<?xml version='1.0' encoding='UTF-8'?>
<hierarchy>
    <node resource-id="button1" text="Click Me" clickable="true"/>
</hierarchy>"""
    mock_u2_device.dump_hierarchy = MagicMock(return_value=sample_xml)

    result = await dump_hierarchy.fn("emulator-5554", xpath="//*[@nonexistent='true']")

    assert result == ""


@pytest.mark.asyncio
@pytest.mark.unit
async def test_dump_hierarchy_with_compressed_and_pretty(mock_u2_device: MagicMock) -> None:
    """Test dump_hierarchy passes compressed and pretty parameters."""
    sample_xml = "<hierarchy><node/></hierarchy>"
    mock_u2_device.dump_hierarchy = MagicMock(return_value=sample_xml)

    await dump_hierarchy.fn("emulator-5554", compressed=True, pretty=True)

    mock_u2_device.dump_hierarchy.assert_called_once_with(compressed=True, pretty=True, max_depth=None)


@pytest.mark.asyncio
@pytest.mark.unit
async def test_dump_hierarchy_with_max_depth(mock_u2_device: MagicMock) -> None:
    """Test dump_hierarchy passes max_depth parameter."""
    sample_xml = "<hierarchy><node/></hierarchy>"
    mock_u2_device.dump_hierarchy = MagicMock(return_value=sample_xml)

    await dump_hierarchy.fn("emulator-5554", max_depth=5)

    mock_u2_device.dump_hierarchy.assert_called_once_with(compressed=False, pretty=False, max_depth=5)


@pytest.mark.asyncio
@pytest.mark.unit
async def test_dump_hierarchy_max_depth_negative_uses_none(mock_u2_device: MagicMock) -> None:
    """Test dump_hierarchy converts negative max_depth to None."""
    sample_xml = "<hierarchy><node/></hierarchy>"
    mock_u2_device.dump_hierarchy = MagicMock(return_value=sample_xml)

    await dump_hierarchy.fn("emulator-5554", max_depth=-1)

    mock_u2_device.dump_hierarchy.assert_called_once_with(compressed=False, pretty=False, max_depth=None)


@pytest.mark.asyncio
@pytest.mark.unit
async def test_save_dump_hierarchy_full(mock_u2_device: MagicMock, tmp_path: Path) -> None:
    """Test save_dump_hierarchy saves full XML when no xpath provided."""
    sample_xml = """<?xml version='1.0' encoding='UTF-8'?>
<hierarchy>
    <node resource-id="button1" text="Click Me"/>
</hierarchy>"""
    mock_u2_device.dump_hierarchy = MagicMock(return_value=sample_xml)

    output_path = tmp_path / "hierarchy.xml"
    result = await save_dump_hierarchy.fn("emulator-5554", str(output_path))

    # Verify file was created and contains the full XML
    assert isinstance(result, str)
    assert "hierarchy.xml" in result
    saved_content = Path(output_path).read_text(encoding="utf-8")
    assert saved_content == sample_xml


@pytest.mark.asyncio
@pytest.mark.unit
async def test_save_dump_hierarchy_with_xpath_filter(mock_u2_device: MagicMock, tmp_path: Path) -> None:
    """Test save_dump_hierarchy saves filtered XML when xpath provided."""
    sample_xml = """<?xml version='1.0' encoding='UTF-8'?>
<hierarchy>
    <node resource-id="button1" text="Click Me" clickable="true"/>
    <node resource-id="button2" text="Don't Click" clickable="false"/>
</hierarchy>"""
    mock_u2_device.dump_hierarchy = MagicMock(return_value=sample_xml)

    output_path = tmp_path / "hierarchy.xml"
    result = await save_dump_hierarchy.fn("emulator-5554", str(output_path), xpath="//*[@clickable='true']")

    # Verify file was created and contains only the filtered element
    assert isinstance(result, str)
    saved_content = Path(output_path).read_text(encoding="utf-8")
    assert 'resource-id="button1"' in saved_content
    assert 'resource-id="button2"' not in saved_content


@pytest.mark.asyncio
@pytest.mark.unit
async def test_save_dump_hierarchy_creates_directory(mock_u2_device: MagicMock, tmp_path: Path) -> None:
    """Test save_dump_hierarchy creates parent directory if it doesn't exist."""
    sample_xml = "<hierarchy><node/></hierarchy>"
    mock_u2_device.dump_hierarchy = MagicMock(return_value=sample_xml)

    output_path = tmp_path / "subdir1" / "subdir2" / "hierarchy.xml"
    result = await save_dump_hierarchy.fn("emulator-5554", str(output_path))

    # Verify file was created in the new subdirectories
    assert isinstance(result, str)
    assert Path(output_path).exists()
    assert Path(output_path).parent.exists()


@pytest.mark.asyncio
@pytest.mark.unit
async def test_save_dump_hierarchy_xpath_no_match_saves_empty(mock_u2_device: MagicMock, tmp_path: Path) -> None:
    """Test save_dump_hierarchy saves empty file when xpath matches nothing."""
    sample_xml = """<?xml version='1.0' encoding='UTF-8'?>
<hierarchy>
    <node resource-id="button1" text="Click Me"/>
</hierarchy>"""
    mock_u2_device.dump_hierarchy = MagicMock(return_value=sample_xml)

    output_path = tmp_path / "hierarchy.xml"
    result = await save_dump_hierarchy.fn("emulator-5554", str(output_path), xpath="//*[@nonexistent='true']")

    # Verify file was created but is empty
    assert isinstance(result, str)
    saved_content = Path(output_path).read_text(encoding="utf-8")
    assert saved_content == ""


@pytest.mark.asyncio
@pytest.mark.unit
async def test_save_dump_hierarchy_returns_absolute_path(mock_u2_device: MagicMock, tmp_path: Path) -> None:
    """Test save_dump_hierarchy returns absolute path."""
    sample_xml = "<hierarchy><node/></hierarchy>"
    mock_u2_device.dump_hierarchy = MagicMock(return_value=sample_xml)

    output_path = tmp_path / "hierarchy.xml"
    result = await save_dump_hierarchy.fn("emulator-5554", str(output_path))

    # Verify result is an absolute path
    assert isinstance(result, str)
    assert Path(result).is_absolute()


@pytest.mark.asyncio
@pytest.mark.unit
async def test_save_dump_hierarchy_default_pretty_true(mock_u2_device: MagicMock, tmp_path: Path) -> None:
    """Test save_dump_hierarchy defaults pretty to True for file output."""
    sample_xml = "<hierarchy><node/></hierarchy>"
    mock_u2_device.dump_hierarchy = MagicMock(return_value=sample_xml)

    output_path = tmp_path / "hierarchy.xml"
    await save_dump_hierarchy.fn("emulator-5554", str(output_path))

    # Verify pretty=True was passed
    mock_u2_device.dump_hierarchy.assert_called_once_with(compressed=False, pretty=True, max_depth=None)
