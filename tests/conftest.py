"""
Pytest configuration and shared fixtures for uiautomator2-mcp-server tests.
"""

from __future__ import annotations

import asyncio
from unittest.mock import MagicMock, patch

import pytest

# Initialize mcp at module import time, before any test modules are imported
# This ensures @mcp.tool() decorators in tool modules work during test collection
from u2mcp.mcp import make_mcp

make_mcp()


@pytest.fixture
def mock_u2_device() -> MagicMock:
    """Create a mocked uiautomator2 device.

    This fixture has function scope, ensuring a fresh mock for each test.
    """

    def create_fresh_device():
        """Helper to create a fresh device mock."""
        mock_device = MagicMock()
        # Setup common device properties
        mock_device.info = {"productName": "test_device", "version": "13", "serial": "emulator-5554"}
        mock_device.device_info = {"serial": "emulator-5554", "model": "test_device"}

        # Setup methods - use MagicMock for methods called with to_thread.run_sync
        mock_device.window_size = MagicMock(return_value=(1080, 2400))
        mock_device.screenshot = MagicMock(return_value=MagicMock())
        mock_device.dump_hierarchy = MagicMock(return_value="<hierarchy/>")
        mock_device.wait_activity = MagicMock(return_value=True)

        # Action methods
        mock_device.click = MagicMock()
        mock_device.long_click = MagicMock()
        mock_device.double_click = MagicMock()
        mock_device.swipe = MagicMock()
        mock_device.swipe_points = MagicMock()
        mock_device.drag = MagicMock()
        mock_device.press = MagicMock()
        mock_device.send_keys = MagicMock()
        mock_device.clear_text = MagicMock()
        mock_device.screen_on = MagicMock()
        mock_device.screen_off = MagicMock()
        mock_device.hide_keyboard = MagicMock()

        # App management methods
        mock_device.app_start = MagicMock()
        mock_device.app_wait = MagicMock(return_value=True)
        mock_device.app_stop = MagicMock()
        mock_device.app_stop_all = MagicMock()
        mock_device.app_info = MagicMock(
            return_value={"packageName": "com.example.app", "versionName": "1.0", "versionCode": 1}
        )
        mock_device.app_current = MagicMock(return_value={"package": "com.example.app"})
        mock_device.app_list = MagicMock(return_value=["com.example.app1", "com.example.app2"])
        mock_device.app_list_running = MagicMock(return_value=["com.example.app1"])
        mock_device.app_install = MagicMock()
        mock_device.app_uninstall = MagicMock(return_value=True)
        mock_device.app_uninstall_all = MagicMock()
        mock_device.app_clear = MagicMock()
        mock_device.app_auto_grant_permissions = MagicMock()

        # Clipboard methods
        mock_device.clipboard = "Sample clipboard text"
        mock_device.set_clipboard = MagicMock()

        # Element/XPath methods
        mock_xpath = MagicMock()
        mock_xpath.wait = MagicMock(return_value=True)
        mock_xpath.wait_gone = MagicMock(return_value=True)
        mock_xpath.click_exists = MagicMock(return_value=True)
        mock_xpath.click_nowait = MagicMock()
        mock_xpath.click_gone = MagicMock(return_value=True)
        mock_xpath.long_click = MagicMock()
        mock_xpath.get_text = MagicMock(return_value="Sample text")
        mock_xpath.set_text = MagicMock()
        mock_xpath.bounds = MagicMock(return_value=(100, 200, 300, 400))
        mock_xpath.swipe = MagicMock()
        mock_xpath.scroll_to = MagicMock(return_value=True)

        # Mock screenshot method
        from PIL.Image import Image

        mock_image = MagicMock(spec=Image)
        mock_image.width = 100
        mock_image.height = 200
        mock_image.save = MagicMock()

        mock_xpath.screenshot = MagicMock(return_value=mock_image)
        mock_device.xpath = MagicMock(return_value=mock_xpath)

        return mock_device

    return create_fresh_device()


@pytest.fixture
def mock_adb() -> MagicMock:
    """Create a mocked adbutils.adb object."""
    mock_adb = MagicMock()
    mock_device = MagicMock()
    mock_device.serial = "emulator-5554"
    mock_device.prop = MagicMock(return_value="test_value")
    mock_adb.device = MagicMock(return_value=mock_device)
    mock_adb.device_list = MagicMock(return_value=[mock_device])
    return mock_adb


@pytest.fixture
def mock_u2_module(mock_u2_device: MagicMock) -> MagicMock:
    """Create a mocked uiautomator2 module."""
    mock_u2 = MagicMock()
    mock_u2.connect = MagicMock(return_value=mock_u2_device)
    mock_u2.Device = MagicMock(return_value=mock_u2_device)
    return mock_u2


@pytest.fixture
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
def mock_device_dependencies(
    mock_u2_device: MagicMock,
    mock_u2_module: MagicMock,
    mock_adb: MagicMock,
):
    """
    Automatically mock uiautomator2 and adbutils dependencies for all tests.

    This ensures tests don't require actual Android devices or ADB connections.

    Note: Each test function receives fresh mock instances through fixtures to avoid
    state pollution between tests. The mock_u2_device fixture is called for each test,
    ensuring clean state.
    """
    # Import here to access the module-level _devices dict
    from u2mcp.tools import device

    # Clear device cache before each test
    device._devices.clear()

    with patch("u2mcp.tools.device.u2", mock_u2_module), patch("u2mcp.tools.device.adb", mock_adb):
        yield

    # Clear device cache after each test
    device._devices.clear()


@pytest.fixture
def mock_context() -> MagicMock:
    """Create a mocked FastMCP context."""
    mock_context = MagicMock()
    mock_context.session = MagicMock()
    mock_context.session.id = "test-session-id"
    return mock_context
