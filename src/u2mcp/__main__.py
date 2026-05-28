"""CLI entrypoint for u2mcp."""

from __future__ import annotations

import asyncio
import logging
import re
import secrets
import sys
import time
from pathlib import Path
from typing import Annotated, Any, Literal

from cyclopts import App, Group, Parameter
from cyclopts.config import Env
from cyclopts.exceptions import ValidationError
from rich.console import Console
from rich.status import Status

from .config import ENV_PREFIX, resolve_config
from .version import __version__


def _load_mcp(console: Console, check_adb: bool = False, **kwargs):
    """Load heavy deps, optionally check ADB, and build MCP server with a spinner."""
    t0 = time.perf_counter()
    status = Status("Loading...", console=console)
    status.start()

    try:
        if check_adb:
            status.update("Checking ADB...")
            from .health import check_adb as _check_adb

            if not _check_adb(console):
                console.print("[yellow]Proceeding anyway. Use --no-check-adb to bypass this check.[/yellow]")

        status.update("Initializing server...")
        from .mcp import make_mcp

        mcp = make_mcp(**kwargs)
    finally:
        status.stop()

    elapsed = time.perf_counter() - t0
    console.print(f"[dim]Ready ({elapsed:.1f}s)[/dim]", highlight=False)
    return mcp


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
    xpath_timeout: Annotated[float, Parameter(name=["--xpath-timeout"])] = 20.0,
    print_tags: bool = True,
    fix_empty_responses: bool = False,
    show_fastmcp_banner: bool | None = None,
):
    """Run the MCP server with stdio transport.

    Args:
        check_adb: Check ADB availability at startup.
        log_level: Log level.
        include_tags: Only expose tools with these tags (comma-separated, supports * and ? wildcards, e.g., device:*,*:shell).
        exclude_tags: Exclude tools with these tags (comma-separated, supports * and ? wildcards, e.g., screen:*,*:mirror).
        xpath_timeout: Default timeout in seconds for XPath element lookup (default: 20.0).
        print_tags: Show enabled tags and tools at startup.
        fix_empty_responses: Convert null tool responses to empty string compatibility.
        show_fastmcp_banner: Show FastMCP banner on startup.
    """
    stderr = Console(stderr=True)
    _setup_logging(log_level)

    mcp = _load_mcp(
        stderr,
        check_adb=check_adb,
        print_tags=print_tags,
        include_tags=include_tags,
        exclude_tags=exclude_tags,
        fix_empty_responses=fix_empty_responses,
        xpath_timeout=xpath_timeout,
    )
    mcp.run(transport="stdio", show_banner=show_fastmcp_banner, log_level=log_level)


@app.command(group=server_group)
def http(
    *,
    host: Annotated[str | None, Parameter(name=["--host", "-H"])] = None,
    port: Annotated[int | None, Parameter(name=["--port", "-p"])] = None,
    token: Annotated[str | None, Parameter(name=["--token", "-t"])] = None,
    auth: bool = True,
    json_response: bool = True,
    check_adb: bool = True,
    log_level: Annotated[
        Literal["debug", "info", "warning", "error", "critical"], Parameter(name=["--log-level", "-l"])
    ] = "info",
    include_tags: Annotated[str | None, Parameter(name=["--include-tags", "-i"])] = None,
    exclude_tags: Annotated[str | None, Parameter(name=["--exclude-tags", "-e"])] = None,
    xpath_timeout: Annotated[float, Parameter(name=["--xpath-timeout"])] = 20.0,
    print_tags: bool = True,
    fix_empty_responses: bool = False,
    show_fastmcp_banner: bool | None = None,
):
    """Run the MCP server with HTTP (streamable-http) transport.

    Args:
        host: Host address to bind to.
        port: Port number to bind to.
        token: Explicit set authentication token.
        auth: Enable authentication. If enabled and no token is set, a random one will be generated.
        json_response: Use JSON response format.
        check_adb: Check ADB availability at startup.
        log_level: Log level.
        include_tags: Only expose tools with these tags (comma-separated, supports * and ? wildcards, e.g., device:*,*:shell).
        exclude_tags: Exclude tools with these tags (comma-separated, supports * and ? wildcards, e.g., screen:*,*:mirror).
        xpath_timeout: Default timeout in seconds for XPath element lookup (default: 20.0).
        print_tags: Show enabled tags and tools at startup.
        fix_empty_responses: Convert null tool responses to empty string compatibility.
        show_fastmcp_banner: Show FastMCP banner on startup.
    """
    stderr = Console(stderr=True)
    _setup_logging(log_level)

    user_provided = bool(token)
    if token:
        token = _validate_token(token)
    elif auth:
        token = secrets.token_urlsafe()

    mcp = _load_mcp(
        stderr,
        check_adb=check_adb,
        token=token,
        user_provided_token=user_provided,
        print_tags=print_tags,
        include_tags=include_tags,
        exclude_tags=exclude_tags,
        fix_empty_responses=fix_empty_responses,
        xpath_timeout=xpath_timeout,
    )
    transport_kwargs: dict[str, Any] = {"log_level": log_level}
    if host is not None:
        transport_kwargs["host"] = host
    if port is not None:
        transport_kwargs["port"] = port
    if json_response:
        transport_kwargs["json_response"] = json_response

    mcp.run(transport="streamable-http", show_banner=show_fastmcp_banner, **transport_kwargs)


@app.command(group=info_group)
def tools():
    """List all available MCP tools."""
    import anyio

    from .helpers import print_tool_help

    console = Console()
    mcp = _load_mcp(console)
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
    import anyio

    from .helpers import print_tool_help

    console = Console()
    mcp = _load_mcp(console)
    anyio.run(lambda: print_tool_help(mcp, console, tool_name))


@app.command(group=info_group)
def tags():
    """List all available tool tags."""
    import anyio

    from .helpers import print_tags as print_tags_from_mcp

    console = Console()
    mcp = _load_mcp(console)
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
    from .health import run_doctor

    sys.exit(run_doctor(verbose=verbose, fix=fix, category=category, exclude=exclude))


env_loader = Env(prefix=ENV_PREFIX)


@app.meta.default
def meta(
    *tokens: Annotated[str, Parameter(show=False, allow_leading_hyphen=True)],
    config_file: Annotated[Path | None, Parameter(name=["--config-file", "-c"])] = None,
):
    """Run the MCP server with configuration from files.

    Args:
        config_file: Path to config file (TOML, YAML, or JSON). Overrides auto-discovery.
    """
    app.config = [*resolve_config(config_file), env_loader]
    app(tokens)


# Env loader for meta-level params (e.g. U2MCP_CONFIG_FILE -> --config-file)
app.meta.config = env_loader


def main():
    """Entry point for the CLI."""
    try:
        app.meta()
    except KeyboardInterrupt:
        pass
    except asyncio.CancelledError:
        pass
    except BaseException as exc:
        # anyio cancel scopes may raise RuntimeError during cancellation
        # when the scope chain is broken by Ctrl-C or stdin close during shutdown.
        # Only suppress if the chain originates from CancelledError or if this is
        # an anyio cancel-scope mismatch (harmless during teardown).
        if isinstance(exc.__context__, asyncio.CancelledError):
            pass
        elif isinstance(exc, RuntimeError) and "cancel scope" in str(exc):
            pass
        else:
            raise exc from None


if __name__ == "__main__":
    main()
