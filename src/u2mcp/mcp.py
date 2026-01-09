"""
This MCP server provides tools for controlling and interacting with Android devices using uiautomator2.

It allows you to perform various operations on Android devices such as connecting to devices, taking screenshots,
getting device information, accessing UI hierarchy, tap on screens, and more...

It also provides tools for managing Android applications, such as installing, uninstalling, starting, stopping, and clearing applications.

Before performing operations on a device, you need to initialize it using the init tool.

All operations require a device serial number to identify the target device.
"""

from contextlib import asynccontextmanager
from textwrap import dedent
from typing import Any

from fastmcp import FastMCP
from rich.console import Console
from rich.markdown import Markdown

__all__ = ["mcp"]

_params: dict[str, Any] = {}


def update_params(**kwargs):
    global _params
    _params.update(kwargs)


@asynccontextmanager
async def _lifespan(instance: FastMCP):
    if _params.get("transport") == "http" and (token := _params.get("token")):
        host = _params.get("host", "HOST")
        port = _params.get("port", "PORT")

        content = dedent(f"""
        ------

        ### Server configured with authentication token. Please connect using one of the following methods:

        - Direct connection: <http://{host}:{port}/mcp?token={token}>

        - Header authentication: <http://{host}:{port}/mcp>

          with header: `Authorization: Bearer {token}`

        ------
        """).strip()
        Console().print(Markdown(content))

    yield


mcp = FastMCP(name="uiautomator2", instructions=__doc__, lifespan=_lifespan)
