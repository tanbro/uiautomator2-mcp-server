"""
This MCP server provides tools for controlling and interacting with Android devices using uiautomator2.

It allows you to perform various operations on Android devices such as connecting to devices, taking screenshots,
getting device information, accessing UI hierarchy, tap on screens, and more...

It also provides tools for managing Android applications, such as installing, uninstalling, starting, stopping, and clearing applications.

Before performing operations on a device, you need to initialize it using the init tool.

All operations require a device serial number to identify the target device.
"""

from __future__ import annotations

import sys
from contextlib import asynccontextmanager
from functools import partial
from textwrap import dedent
from typing import Any

from anyio import create_task_group
from fastmcp import FastMCP
from fastmcp.server.auth import AccessToken, AuthProvider
from pydantic import AnyHttpUrl
from rich.console import Console
from rich.markdown import Markdown

from .background import set_background_task_group
from .helpers import print_tags

if sys.version_info >= (3, 12):  # qa: noqa
    from typing import override
else:  # qa: noqa
    from typing_extensions import override

__all__ = ["mcp", "make_mcp"]


# Warning: You can NOT import it unless call `make_mcp()`
mcp: FastMCP


@asynccontextmanager
async def _lifespan(instance: FastMCP, /, show_tags: bool = True, token: str | None = None):
    console = Console(stderr=True)

    # Show enabled tags and tools if requested
    if show_tags:
        console.print("\n[bold cyan]Enabled Tags and Tools:[/bold cyan]")
        await print_tags(instance, console)
        console.print("")

    if token:
        content = Markdown(
            dedent(f"""
            ------

            Server configured with **authentication token**. Connect using this token in the Authorization header:

            `Authorization: Bearer {token}`

            ------
            """)
        )
        console.print(content)

    # Global task group for background tasks - keeps running until server shuts down
    async with create_task_group() as tg:
        set_background_task_group(tg)
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


def make_mcp(
    token: str | None = None,
    include_tags: set[str] | None = None,
    exclude_tags: set[str] | None = None,
    show_tags: bool = False,
) -> FastMCP:
    global mcp
    params: dict[str, Any] = dict(name="uiautomator2", instructions=__doc__)
    lifespan_kwargs: dict[str, Any] = {"show_tags": show_tags}
    if token:
        lifespan_kwargs["token"] = token
        params.update(lifespan=partial(_lifespan, **lifespan_kwargs), auth=_SimpleTokenAuthProvider(token=token))
    else:
        params.update(lifespan=partial(_lifespan, **lifespan_kwargs))
    if include_tags is not None:
        params["include_tags"] = include_tags
    if exclude_tags is not None:
        params["exclude_tags"] = exclude_tags
    mcp = FastMCP(**params)
    return mcp
