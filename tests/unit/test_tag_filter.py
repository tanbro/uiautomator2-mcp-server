"""Unit tests for tool/tag filtering (list params, native enable/disable)."""

from __future__ import annotations

import io
import json
from pathlib import Path

import pytest
from rich.console import Console

from u2mcp.__main__ import meta
from u2mcp.mcp import _lifespan, _normalize_filter, make_mcp


def make_console() -> Console:
    return Console(file=io.StringIO(), force_terminal=False)


@pytest.mark.unit
class TestNormalizeFilter:
    def test_none_passthrough(self):
        assert _normalize_filter(None) is None

    def test_empty_list_returns_none(self):
        assert _normalize_filter([]) is None

    def test_items_are_stripped(self):
        assert _normalize_filter([" device ", "action:touch"]) == {"device", "action:touch"}

    def test_blank_items_dropped(self):
        assert _normalize_filter(["", "  ", "device"]) == {"device"}

    def test_all_blank_returns_none(self):
        assert _normalize_filter(["", "   "]) is None


async def enabled_names(mcp, **filters) -> set[str]:
    """Enter the lifespan with filters applied and collect enabled tool names."""
    async with _lifespan(mcp, console=make_console(), print_tags=False, **filters):
        tools = await mcp.list_tools()
    return {t.name for t in tools}


@pytest.mark.unit
class TestLifespanFiltering:
    async def test_no_filters_exposes_all(self):
        mcp = make_mcp()
        names = {t.name for t in await mcp.list_tools()}
        assert "click" in names

    async def test_include_tags_allowlist(self):
        names = await enabled_names(make_mcp(), include_tags=["action:touch"])
        assert names == {"click", "long_click", "double_click"}

    async def test_include_bare_category_selects_whole_category(self):
        names = await enabled_names(make_mcp(), include_tags=["clipboard"])
        assert names == {"read_clipboard", "write_clipboard"}

    async def test_exclude_tags_removes_from_full_set(self):
        names = await enabled_names(make_mcp(), exclude_tags=["device:shell"])
        assert "shell_command" not in names
        assert "click" in names

    async def test_exclude_overrides_include(self):
        names = await enabled_names(
            make_mcp(),
            include_tags=["device"],
            exclude_tags=["device:shell"],
        )
        assert "shell_command" not in names
        assert "device_list" in names

    async def test_include_tools_allowlist(self):
        names = await enabled_names(make_mcp(), include_tools=["click", "screenshot"])
        assert names == {"click", "screenshot"}

    async def test_exclude_tools_removes_named_tool(self):
        names = await enabled_names(make_mcp(), exclude_tools=["click"])
        assert "click" not in names
        assert "long_click" in names

    async def test_include_tags_and_tools_are_union(self):
        names = await enabled_names(
            make_mcp(),
            include_tags=["clipboard"],
            include_tools=["click"],
        )
        assert names == {"read_clipboard", "write_clipboard", "click"}

    async def test_exclude_tools_overrides_include_tags(self):
        names = await enabled_names(
            make_mcp(),
            include_tags=["clipboard"],
            exclude_tools=["write_clipboard"],
        )
        assert names == {"read_clipboard"}

    async def test_blank_filter_lists_have_no_effect(self):
        mcp = make_mcp()
        all_names = {t.name for t in await mcp.list_tools()}
        names = await enabled_names(mcp, include_tags=[""], include_tools=[])
        assert names == all_names


@pytest.fixture
def cli_server_mock(mocker):
    """Patch the server constructor so CLI dispatch never starts a server."""
    return mocker.patch("u2mcp.__main__.initial_mcp")


def run_cli(cli_server_mock, *tokens, config_file: Path | None = None):
    """Dispatch CLI tokens through the meta command without running a server."""
    try:
        meta(*tokens, config_file=config_file)
    except SystemExit:
        pass
    assert cli_server_mock.call_count == 1
    return cli_server_mock.call_args.kwargs


@pytest.mark.unit
class TestCliFilterParsing:
    def test_include_tags_repeatable_flags(self, cli_server_mock):
        kwargs = run_cli(cli_server_mock, "stdio", "--include-tags", "device", "--include-tags", "action:touch")
        assert kwargs["include_tags"] == ["device", "action:touch"]

    def test_short_flags(self, cli_server_mock):
        kwargs = run_cli(cli_server_mock, "http", "-i", "device", "-e", "screen:mirror")
        assert kwargs["include_tags"] == ["device"]
        assert kwargs["exclude_tags"] == ["screen:mirror"]

    def test_tool_filter_flags(self, cli_server_mock):
        kwargs = run_cli(
            cli_server_mock,
            "stdio",
            "--include-tools",
            "click",
            "--include-tools",
            "screenshot",
            "--exclude-tools",
            "shell_command",
        )
        assert kwargs["include_tools"] == ["click", "screenshot"]
        assert kwargs["exclude_tools"] == ["shell_command"]

    def test_config_file_list_value(self, cli_server_mock, tmp_path):
        cfg = tmp_path / "u2mcp.json"
        cfg.write_text(json.dumps({"stdio": {"include_tags": ["device", "app:info"]}}))
        kwargs = run_cli(cli_server_mock, "stdio", config_file=cfg)
        assert kwargs["include_tags"] == ["device", "app:info"]

    def test_config_file_kebab_keys(self, cli_server_mock, tmp_path):
        cfg = tmp_path / "u2mcp.json"
        cfg.write_text(json.dumps({"stdio": {"include-tags": ["device"], "exclude-tools": ["shell_command"]}}))
        kwargs = run_cli(cli_server_mock, "stdio", config_file=cfg)
        assert kwargs["include_tags"] == ["device"]
        assert kwargs["exclude_tools"] == ["shell_command"]
