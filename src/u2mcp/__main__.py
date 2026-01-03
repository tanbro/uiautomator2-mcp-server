from __future__ import annotations

import logging
from enum import StrEnum
from typing import Annotated

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


class Transport(StrEnum):
    streamable_http = "streamable-http"
    stdio = "stdio"
    # http = "http"
    # sse = "sse"


def run(
    transport: Annotated[
        Transport, typer.Option("--transport", "-f", help="The transport mechanisms for client-server communication")
    ] = Transport.streamable_http,
    host: Annotated[str | None, typer.Option("--host", "-H", show_default=False, help="Host address for http mode")] = None,
    port: Annotated[int | None, typer.Option("--port", "-p", show_default=False, help="Port number for http mode")] = None,
):
    """Run mcp server
    Args:
        transport (Literal["http", "stdio"]): transport type
        host (str | None): host
        port (int | None): port
    """
    from . import tools as _
    from .mcp import mcp

    if transport == Transport.stdio:
        mcp.run(transport.value)
    elif transport == Transport.streamable_http:
        transport_kwargs = {}
        if host:
            transport_kwargs["host"] = host
        if port:
            transport_kwargs["port"] = port
        mcp.run(transport.value, **transport_kwargs)
    else:
        typer.Abort(f"Unknown transport: {transport}")


def main():
    typer.run(run)


if __name__ == "__main__":
    main()
