"""CLI entrypoint for u2mcp."""

from __future__ import annotations

import logging
import re
import secrets
import sys
from typing import Annotated, Any, Literal

import anyio
from cyclopts import App, Group, Parameter
from cyclopts.exceptions import ValidationError
from rich.console import Console

from .health import check_adb, run_doctor
from .helpers import print_tags as print_tags_from_mcp
from .helpers import print_tool_help
from .mcp import make_mcp
from .version import __version__

# Organize commands into groups
server_group = Group("Server Commands")
info_group = Group("Information Commands")
doctor_group = Group("Diagnostic Commands")

# Create CLI app with cyclopts
app = App(
    name=__package__,
    help_format="rich",
    help="[bold cyan]MCP server[/bold cyan] for [bold green]AI-powered[/bold green] Android device automation via [magenta]uiautomator2[/magenta]",
    version=f"{__package__} {__version__} Python {sys.version}",
)


def _setup_logging(log_level: Literal["debug", "info", "warning", "error", "critical"]):
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


def _check_adb(console: Console, check: bool):
    """Check ADB availability if enabled."""
    if check and not check_adb(console):
        console.print("[yellow]Proceeding anyway. Use --no-check-adb to bypass this check.[/yellow]")


def _validate_token(token: str) -> str:
    """Validate token format."""
    token = token.strip()
    if not re.match(r"^[a-zA-Z0-9\-_.~!$&'()*+,;=:@]{8,64}$", token):
        raise ValidationError("Token must be 8-64 characters long and can only contain URL-safe characters")
    return token


@app.command(group=server_group)
def stdio(
    *,
    check_adb: bool = True,
    log_level: Annotated[
        Literal["debug", "info", "warning", "error", "critical"], Parameter(name=["--log-level", "-l"])
    ] = "info",
    include_tags: Annotated[str | None, Parameter(name=["--include-tags", "-i"])] = None,
    exclude_tags: Annotated[str | None, Parameter(name=["--exclude-tags", "-e"])] = None,
    print_tags: bool = True,
    fix_empty_responses: bool = False,
    show_fastmcp_banner: bool = False,
):
    """Run the MCP server with stdio transport.

    Args:
        check_adb: Check ADB availability at startup.
        log_level: Log level.
        include_tags: Only expose tools with these tags (comma-separated, supports * and ? wildcards, e.g., device:*,*:shell).
        exclude_tags: Exclude tools with these tags (comma-separated, supports * and ? wildcards, e.g., screen:*,*:mirror).
        print_tags: Show enabled tags and tools at startup.
        fix_empty_responses: Convert null tool responses to empty string compatibility.
        show_fastmcp_banner: Show FastMCP banner on startup.
    """
    _setup_logging(log_level)
    _check_adb(Console(stderr=True), check_adb)
    mcp = make_mcp(
        print_tags=print_tags, include_tags=include_tags, exclude_tags=exclude_tags, fix_empty_responses=fix_empty_responses
    )
    mcp.run("stdio", show_fastmcp_banner, log_level=log_level)


@app.command(group=server_group)
def http(
    *,
    host: Annotated[str | None, Parameter(name=["--host", "-H"])] = None,
    port: Annotated[int | None, Parameter(name=["--port", "-p"])] = None,
    token: Annotated[str | None, Parameter(name=["--token", "-t"])] = None,
    no_token: Annotated[bool, Parameter(name=["--no-token", "-n"])] = False,
    json_response: bool = True,
    check_adb: bool = True,
    log_level: Annotated[
        Literal["debug", "info", "warning", "error", "critical"], Parameter(name=["--log-level", "-l"])
    ] = "info",
    include_tags: Annotated[str | None, Parameter(name=["--include-tags", "-i"])] = None,
    exclude_tags: Annotated[str | None, Parameter(name=["--exclude-tags", "-e"])] = None,
    print_tags: bool = True,
    fix_empty_responses: bool = False,
    show_fastmcp_banner: bool = False,
):
    """Run the MCP server with HTTP (streamable-http) transport.

    Args:
        host: Host address to bind to.
        port: Port number to bind to.
        token: Explicit set authentication token.
        no_token: Disable authentication bearer token verification. If not set, a token will be generated randomly.
        json_response: Use JSON response format.
        check_adb: Check ADB availability at startup.
        log_level: Log level.
        include_tags: Only expose tools with these tags (comma-separated, supports * and ? wildcards, e.g., device:*,*:shell).
        exclude_tags: Exclude tools with these tags (comma-separated, supports * and ? wildcards, e.g., screen:*,*:mirror).
        print_tags: Show enabled tags and tools at startup.
        fix_empty_responses: Convert null tool responses to empty string compatibility.
        show_fastmcp_banner: Show FastMCP banner on startup.
    """
    _setup_logging(log_level)
    _check_adb(Console(stderr=True), check_adb)

    if token:
        token = _validate_token(token)
    elif not no_token:
        token = secrets.token_urlsafe()

    transport_kwargs: dict[str, Any] = {"json_response": json_response}
    if host is not None:
        transport_kwargs["host"] = host
    if port is not None:
        transport_kwargs["port"] = port

    mcp = make_mcp(
        token,
        print_tags=print_tags,
        include_tags=include_tags,
        exclude_tags=exclude_tags,
        fix_empty_responses=fix_empty_responses,
    )
    mcp.run("streamable-http", show_fastmcp_banner, **transport_kwargs)


@app.command(group=info_group)
def tools():
    """List all available MCP tools."""
    console = Console()
    mcp = make_mcp()
    anyio.run(lambda: print_tool_help(mcp, console, None))


@app.command(group=info_group)
def info(tool_name: str):
    """Show detailed information about a specific tool.

    Examples:
        u2mcp info screenshot        # Show screenshot tool details
        u2mcp info device:*          # Show all device tools
        u2mcp info "*screenshot*"    # Show tools with 'screenshot' in name

    Args:
        tool_name: Tool name or pattern (supports * and ? wildcards).
    """
    console = Console()
    mcp = make_mcp()
    anyio.run(lambda: print_tool_help(mcp, console, tool_name))


@app.command(group=info_group)
def tags():
    """List all available tool tags."""
    console = Console()
    mcp = make_mcp()
    anyio.run(lambda: print_tags_from_mcp(mcp, console, filtered=False))


@app.command(group=doctor_group)
def doctor(
    *,
    verbose: Annotated[bool, Parameter(name=["--verbose", "-v"])] = False,
    fix: bool = False,
    category: Annotated[str | None, Parameter(name=["--category", "-c"])] = None,
    exclude: Annotated[str | None, Parameter(name=["--exclude"])] = None,
):
    """Run comprehensive diagnostics on the uiautomator2-mcp-server setup.

    Performs checks on:
    - Environment (Python version, platform)
    - ADB availability
    - Device connectivity
    - uiautomator2 initialization
    - MCP tool registration
    - scrcpy availability (optional)

    Args:
        verbose: Show detailed diagnostic output.
        fix: Attempt automatic fixes for issues.
        category: Only check specific categories (comma-separated).
        exclude: Exclude specific categories (comma-separated).

    Returns:
        Exit code: 0 (all passed), 1 (some failed), 2 (doctor error).
    """
    sys.exit(run_doctor(verbose=verbose, fix=fix, category=category, exclude=exclude))


def main():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
