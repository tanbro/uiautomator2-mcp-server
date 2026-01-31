from __future__ import annotations

import logging
import re
import secrets
import sys
from typing import Annotated, Literal

import anyio
import typer
from rich.console import Console

from .health import check_adb
from .helpers import print_tags as print_tags_from_mcp
from .helpers import print_tool_help
from .mcp import make_mcp
from .version import __version__

cli = typer.Typer(
    name="u2mcp",
    help="uiautomator2-mcp-server - MCP server for Android device automation",
    add_completion=False,
    no_args_is_help=True,
)


def _setup_logging(log_level: Literal["debug", "info", "warning", "error", "critical"]) -> None:
    """Configure logging for the MCP server."""
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


def _check_adb(console: Console, skip_check: bool) -> None:
    """Check ADB availability if not skipped."""
    if not skip_check and not check_adb(console):
        console.print("[yellow]Proceeding anyway. Use --skip-adb-check to bypass this check.[/yellow]")


@cli.command("stdio")
def stdio_cmd(
    log_level: Annotated[
        Literal["debug", "info", "warning", "error", "critical"],
        typer.Option("--log-level", "-l", help="Log level"),
    ] = "info",
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
    print_tags: Annotated[
        bool, typer.Option("--print-tags/--no-print-tags", help="Show enabled tags and tools at startup")
    ] = True,
):
    """Run the MCP server with stdio transport."""
    _setup_logging(log_level)
    _check_adb(Console(stderr=True), skip_adb_check)
    mcp = make_mcp(show_tags=print_tags, include_tags=include_tags, exclude_tags=exclude_tags)
    mcp.run(transport="stdio", log_level=log_level)


@cli.command("http")
def http_cmd(
    host: Annotated[str, typer.Option("--host", "-H", show_default="127.0.0.1", help="Host address to bind to")] = "127.0.0.1",
    port: Annotated[int, typer.Option("--port", "-p", show_default="8000", help="Port number to bind to")] = 8000,
    json_response: Annotated[bool, typer.Option("--json-response/--no-json-response", help="Use JSON response format")] = True,
    log_level: Annotated[
        Literal["debug", "info", "warning", "error", "critical"],
        typer.Option("--log-level", "-l", help="Log level"),
    ] = "info",
    no_token: Annotated[
        bool,
        typer.Option(
            "--no-token",
            help="Disable authentication bearer token verification. If not set, a token will be generated randomly.",
        ),
    ] = False,
    token: Annotated[str | None, typer.Option("--token", "-t", help="Explicit set authentication token")] = None,
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
    print_tags: Annotated[
        bool, typer.Option("--print-tags/--no-print-tags", help="Show enabled tags and tools at startup")
    ] = True,
):
    """Run the MCP server with HTTP (streamable-http) transport."""
    _setup_logging(log_level)
    _check_adb(Console(stderr=True), skip_adb_check)

    if token:
        token = token.strip()
        if not re.match(r"^[a-zA-Z0-9\-_.~!$&'()*+,;=:@]{8,64}$", token):
            raise typer.BadParameter("Token must be 8-64 characters long and can only contain URL-safe characters")
    elif not no_token:
        token = secrets.token_urlsafe()

    mcp = make_mcp(token, show_tags=print_tags, include_tags=include_tags, exclude_tags=exclude_tags)
    mcp.run(
        transport="streamable-http",
        host=host,
        port=port,
        json_response=json_response,
        log_level=log_level,
    )


@cli.command("tools")
def tools_cmd():
    """List all available MCP tools."""
    console = Console()
    mcp = make_mcp()
    anyio.run(lambda: print_tool_help(mcp, console, None))


@cli.command("info")
def info_cmd(
    tool_name: Annotated[
        str,
        typer.Argument(help="Tool name or pattern (supports * and ? wildcards)"),
    ],
):
    """Show detailed information about a specific tool.

    Examples:
        u2mcp info screenshot        # Show screenshot tool details
        u2mcp info device:*          # Show all device tools
        u2mcp info "*screenshot*"    # Show tools with 'screenshot' in name
    """
    console = Console()
    mcp = make_mcp()
    anyio.run(lambda: print_tool_help(mcp, console, tool_name))


@cli.command("tags")
def tags_cmd():
    """List all available tool tags."""
    console = Console()
    mcp = make_mcp()
    anyio.run(lambda: print_tags_from_mcp(mcp, console, filtered=False))


@cli.command("version")
def version_cmd():
    """Show version information."""
    typer.echo(f"{__package__} {__version__} (Python {sys.version})")


def main():
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
