"""
This service provides tools for controlling and interacting with Android devices using uiautomator2.

It allows you to perform various operations on Android devices such as connecting to devices, taking screenshots,
getting device information, accessing UI hierarchy, tap on screens, and more...

It also provides tools for managing Android applications, such as installing, uninstalling, starting, stopping, and clearing applications.

Before performing operations on a device, you need to initialize it using the init tool.

All operations require a device serial number to identify the target device.
"""

from fastmcp import FastMCP

__all__ = ["mcp"]

mcp = FastMCP(name="uiautomator2", instructions=__doc__)
