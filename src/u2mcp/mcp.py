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
from fastmcp.server.auth import AccessToken, AuthProvider
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
        content = dedent(f"""
        ------

        **Server configured with authentication token. Connect using this token in the Authorization header:**

        `Authorization: Bearer {token}`

        ------
        """).strip()
        Console().print(Markdown(content))

    yield


class _SimpleTokenAuthProvider(AuthProvider):
    _scopes = ["mcp:tools"]

    async def verify_token(self, token: str) -> AccessToken | None:
        if server_token := _params.get("token"):
            if token == server_token:
                return AccessToken(token=token, client_id="user", scopes=self._scopes)
            return None
        return AccessToken(token=token, client_id="user", scopes=self._scopes)


mcp = FastMCP(name="uiautomator2", instructions=__doc__, lifespan=_lifespan, auth=_SimpleTokenAuthProvider())
