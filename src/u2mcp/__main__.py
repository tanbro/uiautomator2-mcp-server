from __future__ import annotations

import logging
import re
import secrets
import sys
from typing import Annotated, Any, Literal

import typer

from .health import check_adb
from .mcp import make_mcp


def print_version(value: bool):
    """
    Callback function to print the version and exit.
    """
    if value:
        from ._version import __version__

        typer.echo(f"uiautomator2-mcp-server {__version__} (Python {sys.version})")
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
    version: Annotated[
        bool,
        typer.Option("--version", "-V", callback=print_version, is_eager=True, help="Print version information and exit"),
    ] = False,
):
    """Run uiautomator2 mcp server"""
    logging.basicConfig(
        level=log_level.upper(),
        format="[%(asctime)s] %(levelname)s %(name)s - %(message)s",
        handlers=[logging.StreamHandler()],
        force=True,
    )
    logging.getLogger("mcp.server").setLevel(logging.WARNING)
    logging.getLogger("sse_starlette").setLevel(logging.WARNING)
    logging.getLogger("docket").setLevel(logging.WARNING)
    logging.getLogger("fakeredis").setLevel(logging.WARNING)

    # Check ADB availability
    if not skip_adb_check:
        from rich.console import Console

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
        mcp = make_mcp(token)
    else:
        run_kwargs["transport"] = "stdio"
        mcp = make_mcp()

    # can NOT import tools until mcp is crated
    from . import tools as _

    # run mcp
    mcp.run(**run_kwargs)


def main():
    typer.run(run)


if __name__ == "__main__":
    main()
