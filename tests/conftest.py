"""
Pytest configuration and shared fixtures for uiautomator2-mcp-server tests.
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.fixture
def mock_u2_device() -> MagicMock:
    """Create a mocked uiautomator2 device."""
    mock_device = MagicMock()
    # Setup common device methods
    mock_device.info = {"productName": "test_device", "version": "13", "serial": "emulator-5554"}
    mock_device.device_info = {"serial": "emulator-5554", "model": "test_device"}
    mock_device.window_size = MagicMock(return_value=(1080, 2400))
    mock_device.screenshot = MagicMock(return_value=MagicMock())
    mock_device.dump_hierarchy = MagicMock(return_value="<hierarchy/>")
    mock_device.click = AsyncMock()
    mock_device.long_click = AsyncMock()
    mock_device.double_click = AsyncMock()
    mock_device.swipe = AsyncMock()
    mock_device.swipe_points = AsyncMock()
    mock_device.drag = AsyncMock()
    mock_device.press = AsyncMock()
    mock_device.send_keys = AsyncMock()
    mock_device.clear_text = AsyncMock()
    mock_device.screen_on = AsyncMock()
    mock_device.screen_off = AsyncMock()

    # App management methods
    mock_device.app_start = AsyncMock()
    mock_device.app_wait = AsyncMock()
    mock_device.app_stop = AsyncMock()
    mock_device.app_stop_all = AsyncMock()
    mock_device.app_info = MagicMock(return_value={"packageName": "com.example.app", "versionName": "1.0", "versionCode": 1})
    mock_device.app_current = MagicMock(return_value={"package": "com.example.app"})
    mock_device.app_list = MagicMock(return_value=["com.example.app1", "com.example.app2"])
    mock_device.app_list_running = MagicMock(return_value=["com.example.app1"])
    mock_device.app_install = AsyncMock()
    mock_device.app_uninstall = AsyncMock()
    mock_device.app_uninstall_all = AsyncMock()
    mock_device.app_clear = AsyncMock()
    mock_device.app_auto_grant_permissions = AsyncMock()

    return mock_device


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
    """
    with patch("u2mcp.tools.device.u2", mock_u2_module), patch("u2mcp.tools.device.adb", mock_adb):
        yield


@pytest.fixture
def mock_context() -> MagicMock:
    """Create a mocked FastMCP context."""
    mock_context = MagicMock()
    mock_context.session = MagicMock()
    mock_context.session.id = "test-session-id"
    return mock_context
