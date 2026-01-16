"""
This MCP server provides tools for controlling and interacting with Android devices using uiautomator2.

It allows you to perform various operations on Android devices such as connecting to devices, taking screenshots,
getting device information, accessing UI hierarchy, tap on screens, and more...

It also provides tools for managing Android applications, such as installing, uninstalling, starting, stopping, and clearing applications.

Before performing operations on a device, you need to initialize it using the init tool.

All operations require a device serial number to identify the target device.
"""

from contextlib import asynccontextmanager
from functools import partial
from textwrap import dedent
from typing import override

from fastmcp import FastMCP
from fastmcp.server.auth import AccessToken, AuthProvider
from pydantic import AnyHttpUrl
from rich.console import Console
from rich.markdown import Markdown

__all__ = ["mcp", "make_mcp"]


mcp: FastMCP


@asynccontextmanager
async def _lifespan(instance: FastMCP, token: str | None):
    content = Markdown(
        dedent(f"""
        ------

        Server configured with **authentication token**. Connect using this token in the Authorization header:

        `Authorization: Bearer {token}`

        ------
        """).strip()
    )
    Console(stderr=True).print(content)
    yield


class _SimpleTokenAuthProvider(AuthProvider):
    @override
    def __init__(
        self,
        base_url: AnyHttpUrl | str | None = None,
        required_scopes: list[str] | None = ["mcp:tools"],
        token: str | None = None,
    ):
        super().__init__(base_url, required_scopes)
        self.token = token

    @override
    async def verify_token(self, token: str) -> AccessToken | None:
        if self.token == token:
            return AccessToken(token=token, client_id="user", scopes=self.required_scopes)
        return None


def make_mcp(token: str | None = None) -> FastMCP:
    global mcp
    if token:
        _lifespan_callable = partial(_lifespan, token=token)
        mcp = FastMCP(name="uiautomator2", instructions=__doc__, lifespan=_lifespan_callable, auth=_SimpleTokenAuthProvider())
    else:
        mcp = FastMCP(name="uiautomator2", instructions=__doc__)
    return mcp
