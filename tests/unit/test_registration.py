"""Regression tests for the tool inventory reaching a newly created MCP instance.

Tools attach to a server through ``@mcp.tool`` decorators that run at import
time, so a newly created instance only has tools if ``register_tools()``
re-runs them against it. The expected set here is parsed straight out of the
tool modules, which makes it an inventory independent of ``TOOL_MODULES``: a
module dropped from that tuple, or a new tool module never added to it, shows
up as a mismatch.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest
from fastmcp import FastMCP

from u2mcp import tools as tools_package
from u2mcp.mcp import make_mcp

TOOLS_PACKAGE_DIR = Path(tools_package.__file__).resolve().parent


def decorated_tool_names() -> set[str]:
    """Collect every tool name declared by a ``@mcp.tool`` decorator in the package.

    Only the ``@mcp.tool("name", ...)`` form used throughout this package is
    resolved; anything else fails loudly instead of being guessed at.
    """
    declared: list[str] = []
    for module_path in sorted(TOOLS_PACKAGE_DIR.glob("*.py")):
        if module_path.name == "__init__.py":
            continue
        tree = ast.parse(module_path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for decorator in node.decorator_list:
                target = decorator.func if isinstance(decorator, ast.Call) else decorator
                if getattr(target, "attr", "") != "tool":
                    continue
                args = decorator.args if isinstance(decorator, ast.Call) else []
                if args and isinstance(args[0], ast.Constant) and isinstance(args[0].value, str):
                    declared.append(args[0].value)
                else:
                    raise AssertionError(
                        f"{module_path.name}:{decorator.lineno} uses a @mcp.tool form this parser cannot resolve"
                    )
    duplicated = sorted({name for name in declared if declared.count(name) > 1})
    assert not duplicated, f"tool names declared by more than one decorator: {duplicated}"
    return set(declared)


async def registered_tool_names(instance: FastMCP) -> set[str]:
    """List the names of every tool the instance currently exposes."""
    return {tool.name for tool in await instance.list_tools()}


@pytest.mark.unit
class TestToolInventoryRegistration:
    """Pin the decorator-declared tool inventory on freshly created instances."""

    async def test_new_instances_expose_the_decorated_inventory(self) -> None:
        expected = decorated_tool_names()
        assert expected, "no @mcp.tool decorators found; the parser has rotted"

        first = make_mcp()
        second = make_mcp()

        assert await registered_tool_names(first) == expected
        assert await registered_tool_names(second) == expected
