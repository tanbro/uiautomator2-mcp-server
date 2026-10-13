"""
Pytest configuration and shared fixtures for u2mcp-server tests.

Uses pytest-mock (mocker fixture) and pytest's monkeypatch exclusively;
stdlib unittest (including unittest.mock) must not be imported anywhere.
"""

from __future__ import annotations

import pytest
from pytest_mock import MockerFixture

# Initialize mcp at module import time, before any test modules are imported
# This ensures @mcp.tool() decorators in tool modules work during test collection
from u2mcp.mcp import make_mcp

make_mcp()


@pytest.fixture
def mock_u2_device(mocker: MockerFixture):
    """Create a mocked uiautomator2 device.

    This fixture has function scope, ensuring a fresh mock for each test.
    """

    def create_fresh_device():
        """Helper to create a fresh device mock."""
        mock_device = mocker.MagicMock()
        # Setup common device properties
        mock_device.info = {"productName": "test_device", "version": "13", "serial": "emulator-5554"}
        mock_device.device_info = {"serial": "emulator-5554", "model": "test_device"}

        # Setup methods - use MagicMock for methods called with to_thread.run_sync
        mock_device.window_size = mocker.MagicMock(return_value=(1080, 2400))
        mock_device.screenshot = mocker.MagicMock()
        mock_device.dump_hierarchy = mocker.MagicMock(return_value="<hierarchy/>")
        mock_device.wait_activity = mocker.MagicMock(return_value=True)

        # Action methods
        mock_device.click = mocker.MagicMock()
        mock_device.long_click = mocker.MagicMock()
        mock_device.double_click = mocker.MagicMock()
        mock_device.swipe = mocker.MagicMock()
        mock_device.swipe_points = mocker.MagicMock()
        mock_device.drag = mocker.MagicMock()
        mock_device.press = mocker.MagicMock()
        mock_device.send_keys = mocker.MagicMock()
        mock_device.clear_text = mocker.MagicMock()
        mock_device.screen_on = mocker.MagicMock()
        mock_device.screen_off = mocker.MagicMock()
        mock_device.hide_keyboard = mocker.MagicMock()

        # App management methods
        mock_device.app_start = mocker.MagicMock()
        mock_device.app_wait = mocker.MagicMock(return_value=True)
        mock_device.app_stop = mocker.MagicMock()
        mock_device.app_stop_all = mocker.MagicMock()
        mock_device.app_info = mocker.MagicMock(
            return_value={"packageName": "com.example.app", "versionName": "1.0", "versionCode": 1}
        )
        mock_device.app_current = mocker.MagicMock(return_value={"package": "com.example.app"})
        mock_device.app_list = mocker.MagicMock(return_value=["com.example.app1", "com.example.app2"])
        mock_device.app_list_running = mocker.MagicMock(return_value=["com.example.app1"])
        mock_device.app_install = mocker.MagicMock()
        mock_device.app_uninstall = mocker.MagicMock(return_value=True)
        mock_device.app_uninstall_all = mocker.MagicMock()
        mock_device.app_clear = mocker.MagicMock()
        mock_device.app_auto_grant_permissions = mocker.MagicMock()

        # Clipboard methods
        mock_device.clipboard = "Sample clipboard text"
        mock_device.set_clipboard = mocker.MagicMock()

        # Element/XPath methods
        mock_xpath = mocker.MagicMock()
        mock_xpath.wait = mocker.MagicMock(return_value=True)
        mock_xpath.wait_gone = mocker.MagicMock(return_value=True)
        mock_xpath.click_exists = mocker.MagicMock(return_value=True)
        mock_xpath.click_nowait = mocker.MagicMock()
        mock_xpath.click_gone = mocker.MagicMock(return_value=True)
        mock_xpath.long_click = mocker.MagicMock()
        mock_xpath.get_text = mocker.MagicMock(return_value="Sample text")
        mock_xpath.set_text = mocker.MagicMock()
        mock_xpath.bounds = mocker.MagicMock(return_value=(100, 200, 300, 400))
        mock_xpath.swipe = mocker.MagicMock()
        mock_xpath.scroll = mocker.MagicMock(return_value=True)
        mock_xpath.scroll_to = mocker.MagicMock(return_value=True)

        # New v0.3.0 XPath methods
        mock_xpath.exists = True

        # Mock element for get() method (used by xpath_get_info and xpath_get_attrib)
        mock_element = mocker.MagicMock()
        mock_element.info = {
            "text": "Sample",
            "bounds": "(100,200)(300,400)",
            "className": "android.widget.TextView",
            "clickable": True,
        }
        mock_element.attrib = mocker.MagicMock()
        mock_element.attrib.get = mocker.MagicMock(return_value="attribute_value")
        mock_xpath.get = mocker.MagicMock(return_value=mock_element)

        # Mock screenshot method
        from PIL.Image import Image

        mock_image = mocker.MagicMock(spec=Image)
        mock_image.width = 100
        mock_image.height = 200
        mock_image.save = mocker.MagicMock()

        mock_xpath.screenshot = mocker.MagicMock(return_value=mock_image)
        mock_device.xpath = mocker.MagicMock(return_value=mock_xpath)

        return mock_device

    return create_fresh_device()


@pytest.fixture
def mock_adb(mocker: MockerFixture):
    """Create a mocked adbutils.adb object."""
    mock_adb = mocker.MagicMock()
    mock_device = mocker.MagicMock()
    mock_device.serial = "emulator-5554"
    mock_device.prop = mocker.MagicMock(return_value="test_value")
    mock_adb.device = mocker.MagicMock(return_value=mock_device)
    mock_adb.device_list = mocker.MagicMock(return_value=[mock_device])
    return mock_adb


@pytest.fixture
def mock_u2_module(mock_u2_device, mocker: MockerFixture):
    """Create a mocked uiautomator2 module."""
    import uiautomator2

    mock_u2 = mocker.MagicMock()
    mock_u2.connect = mocker.MagicMock(return_value=mock_u2_device)
    mock_u2.Device = mocker.MagicMock(return_value=mock_u2_device)
    # Exception classes must be real so `except u2.ConnectError` works in device.py
    mock_u2.ConnectError = uiautomator2.ConnectError
    return mock_u2


@pytest.fixture(autouse=True)
def mock_device_dependencies(
    mock_u2_device,
    mock_u2_module,
    mock_adb,
    monkeypatch: pytest.MonkeyPatch,
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

    monkeypatch.setattr(device, "u2", mock_u2_module)
    monkeypatch.setattr(device, "adb", mock_adb)
    yield

    # Clear device cache after each test
    device._devices.clear()


@pytest.fixture
def mock_context(mocker: MockerFixture):
    """Create a mocked FastMCP context."""
    mock_context = mocker.MagicMock()
    mock_context.session = mocker.MagicMock()
    mock_context.session.id = "test-session-id"
    return mock_context
