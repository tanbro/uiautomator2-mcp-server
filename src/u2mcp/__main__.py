from __future__ import annotations

import asyncio
import logging
from typing import Annotated, Any, Awaitable, Literal

import typer


def run(
    transport: Annotated[
        Literal["http", "stdio"], typer.Argument(help="Run mcp server on streamable-http http or stdio transport")
    ],
    host: Annotated[
        str | None, typer.Option("--host", "-H", show_default=False, help="Host address of streamable-http mode")
    ] = None,
    port: Annotated[
        int | None, typer.Option("--port", "-p", show_default=False, help="Port number of streamable-http mode")
    ] = None,
    json_response: Annotated[bool, typer.Option("--json-response", "-j", help="Whether to use JSON response format")] = True,
    log_level: Annotated[
        Literal["debug", "info", "warning", "error", "critical"], typer.Option("--log-level", "-l", help="Log level")
    ] = "info",
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
    from .mcp import mcp

    awaitable: Awaitable

    if transport == "http":
        transport_kwargs: dict[str, Any] = {"json_response": json_response}
        if host:
            transport_kwargs["host"] = host
        if port:
            transport_kwargs["port"] = port
        awaitable = mcp.run_http_async(transport="streamable-http", **transport_kwargs, log_level=log_level)

    elif transport == "stdio":
        awaitable = mcp.run_stdio_async(log_level=log_level)

    asyncio.run(asyncio.wait_for(awaitable, None))


def main():
    typer.run(run)


if __name__ == "__main__":
    main()
