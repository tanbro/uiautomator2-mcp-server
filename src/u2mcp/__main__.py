from __future__ import annotations

import logging
import re
import secrets
from typing import Annotated, Any, Literal

import typer


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
            help="Disable token authentication for streamable-http transport. If not set, a token will be generated randomly.",
        ),
    ] = False,
    token: Annotated[
        str | None,
        typer.Option("--token", "-t", help="Explicit set token for streamable-http authentication"),
    ] = None,
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

    from . import tools as _
    from .mcp import mcp, update_params

    transport_kwargs: dict[str, Any] = {"json_response": json_response}

    update_params(transport=transport)

    if transport == "http":
        if token:
            token = token.strip()
            if not re.match(r"^[a-zA-Z0-9\-_.~!$&'()*+,;=:@]{8,64}$", token):
                raise typer.BadParameter("Token must be 8-64 characters long and can only contain URL-safe characters")
        elif not no_token:
            token = secrets.token_urlsafe()
        if token:
            update_params(token=token, host=host, port=port)

        if host:
            transport_kwargs["host"] = host
        if port:
            transport_kwargs["port"] = port

        mcp.run(transport="streamable-http", **transport_kwargs, log_level=log_level)
    else:
        mcp.run(log_level=log_level)


def main():
    typer.run(run)


if __name__ == "__main__":
    main()
