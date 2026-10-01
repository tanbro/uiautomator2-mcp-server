"""
MCP server for Android device automation using uiautomator2.

Run init on the device first for UI and element operations.

Most tools require a device serial number to identify the target device.
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
from rich.progress import Progress

from .background import set_background_task_group
from .helpers import print_tags as async_print_tags
from .middlewares import EmptyResponseMiddleware

if sys.version_info >= (3, 12):  # pragma: no cover
    from typing import override
else:  # pragma: no cover
    from typing_extensions import override

__all__ = ["make_mcp", "mcp"]


# Global MCP instance.
# Initialized by make_mcp() function.
# Do not use before calling make_mcp()
mcp: FastMCP

# Global XPath timeout setting.
# Initialized by make_mcp() function.
_xpath_timeout: float = 20.0


def get_xpath_timeout() -> float:
    """Get the global XPath timeout setting."""
    return _xpath_timeout


def _normalize_filter(values: list[str] | None) -> set[str] | None:
    """Normalize a filter list into a set, returning None when empty."""
    if not values:
        return None
    normalized = {v.strip() for v in values if v.strip()}
    return normalized or None


async def _resolve_tool_names(
    instance: FastMCP,
    tags: list[str] | None,
    tools: list[str] | None,
) -> set[str]:
    """Combine tag and tool filters into the set of tool names they select.

    Tags are matched against the tags of registered tools, so tag and
    tool entries union together.
    """
    tag_set = _normalize_filter(tags)
    tool_set = _normalize_filter(tools)
    if not tag_set:
        return tool_set or set()
    names = set(tool_set) if tool_set else set()
    for tool in await instance.list_tools():
        if (tool.tags or set()) & tag_set:
            names.add(tool.name)
    return names


@asynccontextmanager
async def _lifespan(
    instance: FastMCP,
    /,
    *,
    console: Console,
    progress: Progress | None = None,
    token: str | None = None,
    user_provided_token: bool = False,
    print_tags: bool = True,
    include_tags: list[str] | None = None,
    exclude_tags: list[str] | None = None,
    include_tools: list[str] | None = None,
    exclude_tools: list[str] | None = None,
):

    # Stop the startup spinner
    if progress is not None:
        progress.stop()

    # Apply filters AFTER tools are registered via the native FastMCP
    # enable/disable API: include acts as an allowlist (only=True) and
    # exclude removes from it afterwards, taking precedence. Tags are
    # resolved to tool names first so that tag and tool filters combine
    # as a union (the native API intersects multiple criteria).
    include_names = await _resolve_tool_names(instance, include_tags, include_tools)
    if include_names:
        instance.enable(names=include_names, only=True)
    exclude_names = await _resolve_tool_names(instance, exclude_tags, exclude_tools)
    if exclude_names:
        instance.disable(names=exclude_names)

    # Show enabled tags and tools if requested
    if print_tags:
        console.print("\n[bold cyan]Enabled Tags and Tools:[/bold cyan]")
        await async_print_tags(instance, console)
        console.print("")

    if token:
        if user_provided_token:
            console.print(
                dedent("""\
                [cyan]Authentication enabled. Use your token in the Authorization header as: Bearer <your-token>[/cyan]
                """)
            )
        else:
            content = Markdown(
                dedent(f"""
                ------

                **A random authentication token has been generated.**
                Include it in the `Authorization` header when connecting:

                `Authorization: Bearer {token}`

                - To use your own, restart with `--token YOUR_TOKEN`.
                - To disable authentication, restart with `--no-auth`.
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
        required_scopes: list[str] | None = None,
        token: str | None = None,
    ):
        super().__init__(base_url, required_scopes if required_scopes else ["mcp:tools"])
        self.token = token

    @override
    async def verify_token(self, token: str) -> AccessToken | None:
        if self.token == token:
            return AccessToken(token=token, client_id="user", scopes=self.required_scopes)
        return None


def make_mcp(
    token: str | None = None,
    user_provided_token: bool = False,
    include_tags: list[str] | None = None,
    exclude_tags: list[str] | None = None,
    include_tools: list[str] | None = None,
    exclude_tools: list[str] | None = None,
    print_tags: bool = False,
    fix_empty_responses: bool = False,
    xpath_timeout: float = 20.0,
    progress: Progress | None = None,
    console: Console | None = None,
) -> FastMCP:
    global mcp, _xpath_timeout
    _xpath_timeout = xpath_timeout
    params: dict[str, Any] = {"name": "uiautomator2", "instructions": __doc__}
    lifespan_kwargs: dict[str, Any] = {
        "print_tags": print_tags,
        "include_tags": include_tags,
        "exclude_tags": exclude_tags,
        "include_tools": include_tools,
        "exclude_tools": exclude_tools,
    }
    if token:
        lifespan_kwargs["token"] = token
        lifespan_kwargs["user_provided_token"] = user_provided_token
    if progress is not None:
        lifespan_kwargs["progress"] = progress
    if console is not None:
        lifespan_kwargs["console"] = console
    params.update(lifespan=partial(_lifespan, **lifespan_kwargs))
    if token:
        params["auth"] = _SimpleTokenAuthProvider(token=token)
    mcp = FastMCP(**params)

    # Add middleware to fix empty responses if enabled
    if fix_empty_responses:
        mcp.add_middleware(EmptyResponseMiddleware())

    # Register tools explicitly: importing the tool modules runs their
    # @mcp.tool decorators against the global instance created above.
    from .tools import register_tools

    register_tools()

    return mcp
