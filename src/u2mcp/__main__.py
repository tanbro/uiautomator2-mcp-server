from __future__ import annotations

import asyncio
import logging
from typing import Annotated, Any, Awaitable

import typer

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(name)s - %(message)s",
    handlers=[logging.StreamHandler()],
    force=True,
)

logging.getLogger("mcp.server").setLevel(logging.WARNING)
logging.getLogger("sse_starlette").setLevel(logging.WARNING)
logging.getLogger("docket").setLevel(logging.WARNING)
logging.getLogger("fakeredis").setLevel(logging.WARNING)


def run(
    http: Annotated[bool, typer.Option("--http", "-h", help="Run mcp server in streamable http mode")] = False,
    stdio: Annotated[bool, typer.Option("--stdio", "-s", help="Run mcp server in stdio mode")] = False,
    host: Annotated[str | None, typer.Option("--host", "-H", show_default=False, help="Host address for http mode")] = None,
    port: Annotated[int | None, typer.Option("--port", "-p", show_default=False, help="Port number for http mode")] = None,
    log_level: Annotated[str | None, typer.Option("--log-level", "-l", help="Log level")] = None,
):
    """Run uiautomator2 mcp server"""
    if not http and not stdio:
        typer.Abort("Please specify one of ‘--http’ or ‘--stdio’")

    from . import tools as _
    from .mcp import mcp

    awaitables: list[Awaitable] = []

    if http:
        transport_kwargs: dict[str, Any] = {}
        if host:
            transport_kwargs["host"] = host
        if port:
            transport_kwargs["port"] = port
        awaitables.append(mcp.run_http_async(transport="streamable-http", **transport_kwargs, log_level=log_level))

    if stdio:
        awaitables.append(mcp.run_stdio_async(log_level=log_level))

    async def _run():
        await asyncio.gather(*awaitables)

    asyncio.run(_run())


def main():
    typer.run(run)


if __name__ == "__main__":
    main()
