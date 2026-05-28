"""
MCP server for Android device automation using uiautomator2.

Run init on the device first for UI and element operations.

Most tools require a device serial number to identify the target device.
"""

from __future__ import annotations

import fnmatch
import sys
from contextlib import asynccontextmanager
from functools import partial
from textwrap import dedent
from time import perf_counter
from typing import Any

from anyio import create_task_group
from fastmcp import FastMCP
from fastmcp.server.auth import AccessToken, AuthProvider
from pydantic import AnyHttpUrl
from rich.console import Console
from rich.markdown import Markdown
from rich.status import Status

from .background import set_background_task_group
from .helpers import print_tags as async_print_tags
from .middlewares import EmptyResponseMiddleware

if sys.version_info >= (3, 12):  # pragma: no cover
    from typing import override
else:  # pragma: no cover
    from typing_extensions import override

__all__ = ["mcp", "make_mcp"]


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


def _parse_tags(tags: str | None) -> set[str] | None:
    """Parse comma-separated tags string into a set."""
    if not tags:
        return None
    return {tag.strip() for tag in tags.split(",") if tag.strip()}


def _expand_wildcards(tags: set[str] | None, all_available_tags: set[str] | None) -> set[str] | None:
    """Expand wildcard patterns in tags.

    Supports:
    - *  matches any characters
    - ?  matches exactly one character
    - device:*  matches all device:* tags
    - *:shell  matches all shell tags (device:shell, etc.)

    Examples:
        device:* -> device:manage, device:info, device:capture, device:shell
        *:shell -> device:shell
        action:to* -> action:touch, action:tool (if exists)
    """
    if not tags or not all_available_tags:
        return None

    expanded = set()

    for tag in tags:
        if "*" in tag or "?" in tag:
            # Use fnmatch for wildcard matching
            for existing_tag in all_available_tags:
                if fnmatch.fnmatch(existing_tag, tag):
                    expanded.add(existing_tag)
        else:
            # No wildcard, add as-is
            expanded.add(tag)

    return expanded if expanded else None


@asynccontextmanager
async def _lifespan(
    instance: FastMCP,
    /,
    *,
    token: str | None = None,
    user_provided_token: bool = False,
    print_tags: bool = True,
    include_tags: str | None = None,
    exclude_tags: str | None = None,
    show_auth_info: bool = False,
    console: Console | None = None,
    status: Status | None = None,
    t0: float | None = None,
):
    if console is None:
        console = Console(stderr=True)

    # Stop the startup spinner and show ready time
    if status is not None:
        status.stop()
        if t0 is not None:
            elapsed = perf_counter() - t0
            console.print(f"[dim]Ready ({elapsed:.1f}s)[/dim]", highlight=False)

    # Apply tag filters AFTER tools are registered (v3 API)
    if include_tags is not None or exclude_tags is not None:
        all_tools = await instance.list_tools()
        all_tag_set: set[str] = set()
        for tool in all_tools:
            all_tag_set.update(tool.tags or [])

        parsed_include_tags = _expand_wildcards(_parse_tags(include_tags), all_tag_set)
        parsed_exclude_tags = _expand_wildcards(_parse_tags(exclude_tags), all_tag_set)

        if parsed_include_tags is not None:
            instance.enable(tags=parsed_include_tags, only=True)
        if parsed_exclude_tags is not None:
            instance.disable(tags=parsed_exclude_tags)

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
    elif show_auth_info:
        console.print(
            dedent("""\
            [yellow][bold]Warning[/bold]: Authentication disabled. The server is accessible without a token.[/yellow]
            """)
        )

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
    user_provided_token: bool = False,
    include_tags: str | None = None,
    exclude_tags: str | None = None,
    print_tags: bool = False,
    fix_empty_responses: bool = False,
    xpath_timeout: float = 20.0,
    status: Status | None = None,
    t0: float = 0.0,
    console: Console | None = None,
) -> FastMCP:
    global mcp, _xpath_timeout
    _xpath_timeout = xpath_timeout
    params: dict[str, Any] = dict(name="uiautomator2", instructions=__doc__)
    lifespan_kwargs: dict[str, Any] = {
        "print_tags": print_tags,
        "include_tags": include_tags,
        "exclude_tags": exclude_tags,
    }
    if token:
        lifespan_kwargs["token"] = token
        lifespan_kwargs["user_provided_token"] = user_provided_token
    if status is not None:
        lifespan_kwargs["status"] = status
        lifespan_kwargs["t0"] = t0
    if console is not None:
        lifespan_kwargs["console"] = console
    params.update(lifespan=partial(_lifespan, **lifespan_kwargs))
    if token:
        params["auth"] = _SimpleTokenAuthProvider(token=token)
    mcp = FastMCP(**params)

    # Add middleware to fix empty responses if enabled
    if fix_empty_responses:
        mcp.add_middleware(EmptyResponseMiddleware())

    # Import tools to register them with the MCP
    from . import tools as _  # noqa: F401

    return mcp
