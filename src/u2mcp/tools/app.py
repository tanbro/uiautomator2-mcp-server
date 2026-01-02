from __future__ import annotations

import asyncio
from typing import Any

from ..mcp import mcp
from .device import get_device

__all__ = (
    "app_install",
    "app_uninstall",
    "app_uninstall_all",
    "app_start",
    "app_stop",
    "app_stop_all",
    "app_clear",
    "app_info",
    "app_current",
    "app_list",
    "app_list_running",
    "app_auto_grant_permissions",
)


@mcp.tool("app_install")
def app_install(serial: str, data: str):
    """Install app

    Args:
        data (str): can be file path or url or file object
    """
    device = get_device(serial)
    device.app_install(data)


@mcp.tool("app_uninstall")
def app_uninstall(serial: str, package_name: str) -> bool:
    """Uninstall an app

    Args:
        serial (str): Android device serialno
        package_name (str): package name

    Returns:
        bool: success
    """
    device = get_device(serial)
    return device.app_uninstall(package_name)


@mcp.tool("app_uninstall_all")
def app_uninstall_all(serial: str, excludes: list[str] | None = None) -> list[str]:
    """Uninstall all apps

    Args:
        serial (str): Android device serialno
        excludes (list[str] | None): packages that do not want to uninstall

    Returns:
        list[str]: list of uninstalled apps
    """
    device = get_device(serial)
    return device.app_uninstall_all(excludes or [])


@mcp.tool("app_start")
def app_start(
    serial: str,
    package_name: str,
    activity: str | None = None,
    wait: bool = False,
    stop: bool = False,
):
    """Launch application

    Args:
        serial (str): Android device serialno
        package_name (str): package name
        activity (str): app activity
        stop (bool): Stop app before starting the activity. (require activity)
        wait (bool): wait until app started. default False
    """
    device = get_device(serial)
    device.app_start("com.tencent.mm")


@mcp.tool("app_wait")
async def app_wait(serial: str, package_name: str, timeout: float = 20.0, front=False) -> int:
    """Wait until app launched

    Args:
        serial (str): Android device serialno
        package_name (str): package name
        timeout (float): maximum wait time seconds
        front (bool): wait until app is current app

    Returns:
        pid (int) 0 if launch failed
    """
    device = get_device(serial)
    return await asyncio.to_thread(device.app_wait, package_name, timeout, front)


@mcp.tool("app_stop")
def app_stop(serial: str, package_name: str):
    """Stop one application

    Args:
        serial (str): Android device serialno
        package_name (str): package name
    """
    device = get_device(serial)
    device.app_stop(package_name)


@mcp.tool("app_stop_all")
def app_stop_all(serial: str, excludes: list[str] | None = None) -> list[str]:
    """Stop all third party applications

    Args:
        excludes (list): apps that do now want to kill

    Returns:
        list[str]: a list of killed apps
    """
    device = get_device(serial)
    return device.app_stop_all(excludes or [])


@mcp.tool("app_clear")
def app_clear(serial: str, package_name: str):
    """Stop and clear app data: pm clear

    Args:
        serial (str): Android device serialno
        package_name (str): package name

    Returns:
        bool: success
    """
    device = get_device(serial)
    device.app_clear(package_name)


@mcp.tool("app_info")
def app_info(serial: str, package_name: str) -> dict[str, Any]:
    """
    Get app info

    Args:
        serial (str): Android device serialno
        package_name (str): package name

    Returns:
        dict[str,Any]: app info

        Example:
            {"versionName": "1.1.7", "versionCode": 1001007}
    """
    device = get_device(serial)
    return device.app_info(package_name)


@mcp.tool("app_current")
def app_current(serial: str) -> dict[str, Any]:
    """
    Get current app info

    Args:
        serial (str): Android device serialno

    Returns:
        dict[str,Any]: running app info
    """
    device = get_device(serial)
    return device.app_current()


@mcp.tool("app_list")
def app_list(serial: str, filter: str | None = None) -> list[str]:
    """
    List installed app package names

    Args:
        serial (str): Android device serialno
        filter (str|None): [-f] [-d] [-e] [-s] [-3] [-i] [-u] [--user USER_ID] [FILTER]

    Returns:
        list[str]: list of apps by filter
    """
    device = get_device(serial)
    return device.app_list(filter)  # type: ignore


@mcp.tool("app_list_running")
def app_list_running(serial: str) -> list[str]:
    """
    List running apps

    Args:
        serial (str): Android device serialno

    Returns:
        list[str]: list of running apps
    """
    device = get_device(serial)
    return device.app_list_running()


@mcp.tool("app_auto_grant_permissions")
def app_auto_grant_permissions(serial: str, package_name: str):
    """auto grant permissions

    Args:
        serial (str): Android device serialno
        package_name (str): package name

    Help of "adb shell pm":
        grant [--user USER_ID] PACKAGE PERMISSION
        revoke [--user USER_ID] PACKAGE PERMISSION
            These commands either grant or revoke permissions to apps.  The permissions
            must be declared as used in the app's manifest, be runtime permissions
            (protection level dangerous), and the app targeting SDK greater than Lollipop MR1 (API level 22).

    Help of "Android official pm" see <https://developer.android.com/tools/adb#pm>
        Grant a permission to an app. On devices running Android 6.0 (API level 23) and higher,
            the permission can be any permission declared in the app manifest.
        On devices running Android 5.1 (API level 22) and lower,
            must be an optional permission defined by the app.
    """
    device = get_device(serial)
    device.app_auto_grant_permissions(package_name)
