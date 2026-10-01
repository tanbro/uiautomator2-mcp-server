"""Tool modules registry for the MCP server.

Each tool module registers its functions with the global server instance via
the ``@mcp.tool`` decorator at import time. Importing this package alone
registers nothing; call :func:`register_tools` after ``u2mcp.mcp.make_mcp``
has created the global instance.
"""

from __future__ import annotations


def register_tools() -> None:
    """Import all tool modules so their decorators register on the server.

    Must be called after ``u2mcp.mcp.make_mcp`` has initialized the global
    ``mcp`` instance, otherwise the tool modules fail to import.
    """
    from . import (
        action,
        app,
        clipboard,
        delay,
        device,
        gesture,
        input,
        scrcpy,
        screenrecord,
        system,
        toast,
        xpath,
    )
