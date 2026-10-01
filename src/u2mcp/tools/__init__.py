"""Tool modules registry for the MCP server.

Each tool module registers its functions with the global server instance via
the ``@mcp.tool`` decorator at import time. Importing this package alone
registers nothing; call :func:`register_tools` after ``u2mcp.mcp.make_mcp``
has created the global instance.
"""

from __future__ import annotations

import importlib
import sys

TOOL_MODULES = (
    "action",
    "app",
    "clipboard",
    "delay",
    "device",
    "gesture",
    "input",
    "scrcpy",
    "screenrecord",
    "system",
    "toast",
    "xpath",
)

# Modules whose decorators have already run against a (previous) server
# instance; these must be reloaded on subsequent make_mcp() calls.
_registered_modules: set[str] = set()


def register_tools() -> None:
    """Register all tool modules on the current global server instance.

    Must be called after ``u2mcp.mcp.make_mcp`` has initialized the global
    ``mcp`` instance, otherwise the tool modules fail to import.

    Modules registered against an earlier instance are reloaded so their
    ``@mcp.tool`` decorators run against the current one; otherwise a
    second server would end up with no tools. Modules imported only
    transitively (e.g. ``device`` via ``action``) already ran against the
    current instance and must not be reloaded.
    """
    for name in TOOL_MODULES:
        qualname = f"{__package__}.{name}"
        if name in _registered_modules:
            importlib.reload(sys.modules[qualname])
        elif qualname in sys.modules:
            _registered_modules.add(name)
        else:
            importlib.import_module(qualname)
            _registered_modules.add(name)
