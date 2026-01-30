from __future__ import annotations

import fnmatch
import logging
import re
import secrets
import sys
from typing import Annotated, Any, Literal

import anyio
import typer
from rich.console import Console

from .health import check_adb
from .helpers import print_tags as print_tags_from_mcp
from .mcp import make_mcp
from .version import __version__


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


def print_version(value: bool):
    """
    Callback function to print the version and exit.
    """
    if value:
        typer.echo(f"uiautomator2-mcp-server {__version__} (Python {sys.version})")
        raise typer.Exit()


def print_tags(value: bool):
    """
    Callback function to print all available tags and exit.
    """
    if value:
        console = Console()

        # Create a temporary MCP instance to collect tool tags
        mcp = make_mcp()

        # Import tools to register them
        from . import tools as _

        anyio.run(print_tags_from_mcp, mcp, console)
        raise typer.Exit()


def run(
    transport: Annotated[
        Literal["http", "stdio"], typer.Argument(help="Run mcp server on streamable-http http or stdio transport")
    ] = "stdio",
    host: Annotated[
        str, typer.Option("--host", "-H", show_default=False, help="Host address of streamable-http transport")
    ] = "127.0.0.1",
    port: Annotated[
        int, typer.Option("--port", "-p", show_default=False, help="Port number of streamable-http transport")
    ] = 8000,
    json_response: Annotated[bool, typer.Option("--json-response", "-j", help="Whether to use JSON response format")] = True,
    log_level: Annotated[
        Literal["debug", "info", "warning", "error", "critical"], typer.Option("--log-level", "-l", help="Log level")
    ] = "info",
    no_token: Annotated[
        bool,
        typer.Option(
            "--no-token",
            help="Disable authentication bearer token verification of streamable-http transport. If not set, a token will be generated randomly.",
        ),
    ] = False,
    token: Annotated[
        str | None,
        typer.Option("--token", "-t", help="Explicit set token of streamable-http authentication"),
    ] = None,
    skip_adb_check: Annotated[bool, typer.Option("--skip-adb-check", help="Skip ADB availability check at startup")] = False,
    include_tags: Annotated[
        str | None,
        typer.Option(
            "--include-tags",
            help="Only expose tools with these tags (comma-separated, supports * and ? wildcards, e.g., device:*,*:shell)",
        ),
    ] = None,
    exclude_tags: Annotated[
        str | None,
        typer.Option(
            "--exclude-tags",
            help="Exclude tools with these tags (comma-separated, supports * and ? wildcards, e.g., screen:*,*:mirror)",
        ),
    ] = None,
    list_tags: Annotated[
        bool,
        typer.Option("--list-tags", callback=print_tags, is_eager=True, help="List all available tool tags and exit"),
    ] = False,
    print_tags: Annotated[
        bool,
        typer.Option("--print-tags/--no-print-tags", help="Show enabled tags and tools at startup"),
    ] = True,
    version: Annotated[
        bool,
        typer.Option("--version", "-V", callback=print_version, is_eager=True, help="Print version information and exit"),
    ] = False,
):
    """Run uiautomator2 mcp server"""
    logging.basicConfig(
        level=log_level.upper(),
        format="[%(asctime)s] %(levelname)8s %(name)s - %(message)s",
        handlers=[logging.StreamHandler()],
        force=True,
    )
    logging.getLogger("mcp.server").setLevel(logging.WARNING)
    logging.getLogger("sse_starlette").setLevel(logging.WARNING)
    logging.getLogger("docket").setLevel(logging.WARNING)
    logging.getLogger("fakeredis").setLevel(logging.WARNING)

    # Check ADB availability
    if not skip_adb_check:
        console = Console(stderr=True)
        if not check_adb(console):
            console.print("[yellow]Proceeding anyway. Use --skip-check to bypass this check.[/yellow]")

    run_kwargs: dict[str, Any] = {"log_level": log_level}

    if transport == "http":
        run_kwargs.update({"transport": "streamable-http", "json_response": json_response})
        if host:
            run_kwargs["host"] = host
        if port:
            run_kwargs["port"] = port
        if token:
            token = token.strip()
            if not re.match(r"^[a-zA-Z0-9\-_.~!$&'()*+,;=:@]{8,64}$", token):
                raise typer.BadParameter("Token must be 8-64 characters long and can only contain URL-safe characters")
        elif not no_token:
            token = secrets.token_urlsafe()
        mcp = make_mcp(token, show_tags=print_tags)
    else:
        run_kwargs["transport"] = "stdio"
        mcp = make_mcp(show_tags=print_tags)

    # Import tools to register them with the MCP
    from . import tools as _

    # Collect all available tags from registered tools for wildcard expansion
    all_tag_set = set()
    for tool in mcp._tool_manager._tools.values():
        all_tag_set.update(tool.tags or [])

    # Parse and expand tag filters
    parsed_include_tags = _expand_wildcards(_parse_tags(include_tags), all_tag_set)
    parsed_exclude_tags = _expand_wildcards(_parse_tags(exclude_tags), all_tag_set)

    # Set tag filters on the MCP instance (can be set after creation)
    if parsed_include_tags is not None:
        mcp.include_tags = parsed_include_tags
    if parsed_exclude_tags is not None:
        mcp.exclude_tags = parsed_exclude_tags

    # run mcp
    mcp.run(**run_kwargs)


def main():
    typer.run(run)


if __name__ == "__main__":
    main()
