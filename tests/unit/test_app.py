"""
Unit tests for app management tools.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from u2mcp.tools.app import (
    app_auto_grant_permissions,
    app_clear,
    app_current,
    app_info,
    app_install,
    app_list,
    app_list_running,
    app_start,
    app_stop,
    app_stop_all,
    app_uninstall,
    app_uninstall_all,
    app_wait,
)


@pytest.mark.asyncio
@pytest.mark.unit
async def test_app_install(mock_u2_device: MagicMock) -> None:
    """Test app_install executes without error."""
    await app_install.fn("emulator-5554", "/path/to/app.apk")


@pytest.mark.asyncio
@pytest.mark.unit
async def test_app_uninstall(mock_u2_device: MagicMock) -> None:
    """Test app_uninstall executes without error."""
    await app_uninstall.fn("emulator-5554", "com.example.app")


@pytest.mark.asyncio
@pytest.mark.unit
async def test_app_uninstall_all(mock_u2_device: MagicMock) -> None:
    """Test app_uninstall_all executes without error."""
    await app_uninstall_all.fn("emulator-5554", ["com.system.app"])


@pytest.mark.asyncio
@pytest.mark.unit
async def test_app_start(mock_u2_device: MagicMock) -> None:
    """Test app_start executes without error."""
    await app_start.fn("emulator-5554", "com.example.app")


@pytest.mark.asyncio
@pytest.mark.unit
async def test_app_wait(mock_u2_device: MagicMock) -> None:
    """Test app_wait executes without error."""
    await app_wait.fn("emulator-5554", "com.example.app", timeout=10.0)


@pytest.mark.asyncio
@pytest.mark.unit
async def test_app_stop(mock_u2_device: MagicMock) -> None:
    """Test app_stop executes without error."""
    await app_stop.fn("emulator-5554", "com.example.app")


@pytest.mark.asyncio
@pytest.mark.unit
async def test_app_stop_all(mock_u2_device: MagicMock) -> None:
    """Test app_stop_all executes without error."""
    await app_stop_all.fn("emulator-5554")


@pytest.mark.asyncio
@pytest.mark.unit
async def test_app_clear(mock_u2_device: MagicMock) -> None:
    """Test app_clear executes without error."""
    await app_clear.fn("emulator-5554", "com.example.app")


@pytest.mark.asyncio
@pytest.mark.unit
async def test_app_info(mock_u2_device: MagicMock) -> None:
    """Test app_info executes without error."""
    await app_info.fn("emulator-5554", "com.example.app")


@pytest.mark.asyncio
@pytest.mark.unit
async def test_app_current(mock_u2_device: MagicMock) -> None:
    """Test app_current executes without error."""
    await app_current.fn("emulator-5554")


@pytest.mark.asyncio
@pytest.mark.unit
async def test_app_list(mock_u2_device: MagicMock) -> None:
    """Test app_list executes without error."""
    await app_list.fn("emulator-5554")


@pytest.mark.asyncio
@pytest.mark.unit
async def test_app_list_running(mock_u2_device: MagicMock) -> None:
    """Test app_list_running executes without error."""
    await app_list_running.fn("emulator-5554")


@pytest.mark.asyncio
@pytest.mark.unit
async def test_app_auto_grant_permissions(mock_u2_device: MagicMock) -> None:
    """Test app_auto_grant_permissions executes without error."""
    await app_auto_grant_permissions.fn("emulator-5554", "com.example.app")
