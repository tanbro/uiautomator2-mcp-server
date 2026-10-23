"""Unit tests for the CLI documentation helpers.

These guard the fact that FastMCP strips the Args section out of
``tool.description`` while building the JSON schema, so the CLI renderer has to
read the undecorated docstring and take value domains from the schema.
"""

from __future__ import annotations

import asyncio
import io
import re
from typing import Any

import pytest
from rich.console import Console

from u2mcp.helpers import print_single_tool_help
from u2mcp.mcp import make_mcp


@pytest.fixture(scope="module")
def tools_by_name() -> dict[str, Any]:
    """All registered MCP tools, keyed by tool name."""
    return {tool.name: tool for tool in asyncio.run(make_mcp().list_tools())}


def render(tool: Any) -> str:
    """Render a tool's CLI help panel as whitespace-normalized text."""
    buffer = io.StringIO()
    console = Console(file=buffer, width=200, force_terminal=False)
    print_single_tool_help(console, tool.name, tool)
    return re.sub(r"\s+", " ", buffer.getvalue())


@pytest.mark.unit
def test_description_does_not_carry_the_args_section(tools_by_name: dict[str, Any]) -> None:
    """Pin the FastMCP behaviour the renderer works around."""
    tool = tools_by_name["xpath_scroll_to"]
    assert "Args:" in tool.fn.__doc__
    assert "Args:" not in tool.description


@pytest.mark.unit
def test_info_lists_parameters(tools_by_name: dict[str, Any]) -> None:
    """Rendered help shows every documented parameter with its type."""
    out = render(tools_by_name["xpath_scroll_to"])
    assert "direction (SwipeDirectionType): Swipe direction." in out
    assert "max_swipes (int): Maximum swipe attempts." in out


@pytest.mark.unit
def test_info_takes_value_domains_from_the_schema(tools_by_name: dict[str, Any]) -> None:
    """Docstrings no longer list values, so the schema enum has to."""
    out = render(tools_by_name["xpath_scroll_to"])
    assert "one of: left, right, up, down" in out
    assert "default: 10" in out


@pytest.mark.unit
def test_info_shows_schema_enum_without_default(tools_by_name: dict[str, Any]) -> None:
    """A required enum parameter shows its domain and no default."""
    out = render(tools_by_name["xpath_swipe"])
    assert "direction (SwipeDirectionType): Swipe direction. (one of: left, right, up, down)" in out


@pytest.mark.unit
def test_info_lists_returns_section(tools_by_name: dict[str, Any]) -> None:
    """The Returns block from the docstring reaches the CLI."""
    out = render(tools_by_name["xpath_scroll"])
    assert "Returns:" in out
    assert "True if can scroll further" in out
