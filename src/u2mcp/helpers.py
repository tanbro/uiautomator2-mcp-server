"""Helper functions for u2mcp."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from docstring_parser import parse
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

if TYPE_CHECKING:
    from .mcp import FastMCP


__all__ = ["print_tags", "print_tool_help"]


async def print_tags(instance: FastMCP, console: Console, *, filtered: bool = True):
    """Print tags from an MCP instance.

    Args:
        instance: The MCP instance to get tools from
        console: The Rich console to print to
        filtered: If True, only show tags that match include/exclude filters.
                   If False, show all available tags. Defaults to True.
    """
    tags_map: dict[str, list[str]] = {}
    # In v3, tag filters are applied via enable/disable, not stored as attributes
    # We'll show all tools since filtering is handled by the server itself
    include_tags = None
    exclude_tags = None

    # list_tools() returns list in v3, not dict
    for tool in await instance.list_tools():
        # Skip tools with no tags
        if not tool.tags:
            continue

        # Apply include filter
        if include_tags is not None and not any(tag in include_tags for tag in tool.tags):
            continue

        # Apply exclude filter
        if exclude_tags is not None and any(tag in exclude_tags for tag in tool.tags):
            continue

        for tag in tool.tags:
            # Only include tags that pass the filters
            if include_tags is not None and tag not in include_tags:
                continue
            if exclude_tags is not None and tag in exclude_tags:
                continue

            if tag not in tags_map:
                tags_map[tag] = []
            tags_map[tag].append(tool.name)

    # Sort tags by category
    sorted_tags = sorted(tags_map.keys())

    # Group by category
    categories: dict[str, list[tuple[str, list[str]]]] = {}
    for tag in sorted_tags:
        if ":" in tag:
            category, subcategory = tag.split(":", 1)
            if category not in categories:
                categories[category] = []
            categories[category].append((subcategory, tags_map[tag]))
        else:
            # Tags without category (if any)
            if "" not in categories:
                categories[""] = []
            categories[""].append((tag, tags_map[tag]))

    # Print table for each category
    for category in sorted(categories.keys()):
        if category == "":
            console.print("\n[bold]Other Tags:[/bold]")
        else:
            console.print(f"\n[bold]{category.title()} Tags:[/bold]")

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Tag", style="cyan", width=20)
        table.add_column("Tools", style="green")

        for subcategory, tools in sorted(categories[category]):
            tag_name = f"{category}:{subcategory}" if category else subcategory
            tools_str = ", ".join(sorted(tools))
            table.add_row(tag_name, tools_str)

        console.print(table)

    console.print(f"\n[bold]Total: {len(tags_map)} tags, {sum(len(v) for v in tags_map.values())} tool-tag assignments[/bold]")

    # Note: In v3, filtering is handled by the server's enable/disable methods
    # The tools returned by list_tools() are already filtered


async def print_tool_help(instance: FastMCP, console: Console, tool_name: str | None = None):
    """Print help information for MCP tools.

    Args:
        instance: The MCP instance to get tools from
        console: The Rich console to print to
        tool_name: If specified, show help for tools matching the pattern.
                   Can be a tool name pattern or a tag pattern (e.g., device:*).
                   If None, list all available tools. Supports * and ? wildcards.
    """
    import fnmatch

    # list_tools() returns list in v3, not dict
    tools_list = await instance.list_tools()

    if tool_name:
        # Filter tools by name pattern OR tag pattern
        matched_tools: list = []
        for tool in tools_list:
            # Check if tool name matches pattern
            if fnmatch.fnmatch(tool.name, tool_name):
                matched_tools.append(tool)
                continue

            # Check if any tag matches pattern
            if tool.tags:
                for tag in tool.tags:
                    if fnmatch.fnmatch(tag, tool_name):
                        matched_tools.append(tool)
                        break

        if not matched_tools:
            console.print(f"[red]No tools found matching pattern: {tool_name}[/red]")
            console.print("[dim]Tip: Use 'u2mcp tools' (no arguments) to list all tools.[/dim]")
            console.print("[dim]Tip: Use 'u2mcp tags' to list all available tags.[/dim]")
            return

        for tool in sorted(matched_tools, key=lambda t: t.name):
            _print_single_tool_help(console, tool.name, tool)
    else:
        # List all tools
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Tool Name", style="cyan", width=25)
        table.add_column("Description", style="white")
        table.add_column("Tags", style="green", width=30)

        for tool in sorted(tools_list, key=lambda t: t.name):
            tags_str = ", ".join(sorted(tool.tags or [])) if tool.tags else ""
            # Extract short description only, skip Args/Returns sections
            description = tool.description or ""
            parsed = parse(description)
            # Use short description, fall back to full description truncated
            desc = parsed.short_description if parsed.short_description else description
            # Truncate if too long
            desc = desc[:57] + "..." if len(desc) > 60 else desc
            table.add_row(tool.name, desc, tags_str)

        console.print("\n[bold cyan]Available Tools:[/bold cyan]")
        console.print(table)
        console.print(f"\n[dim]Total: {len(tools_list)} tools[/dim]")
        console.print("\n[dim]Use 'u2mcp info <tool_name>' for detailed information about a specific tool.[/dim]")
        console.print("[dim]Supports wildcards: 'u2mcp info device:*' (by tag) or 'u2mcp info *screenshot*' (by name)[/dim]")


def _print_single_tool_help(console: Console, name: str, tool: Any):
    """Print detailed help for a single tool.

    Parses doc-strings and formats Args/Returns with markdown.
    """
    # Build markdown content
    md_lines = []

    # Title and tags (as plain text, not markdown)
    tags_str = f"**Tags:** {', '.join(sorted(tool.tags))}" if tool.tags else ""

    # Parse the docstring
    description = tool.description or ""
    parsed = parse(description)

    # Short description
    if parsed.short_description:
        md_lines.append(parsed.short_description)

    # Long description
    if parsed.long_description:
        md_lines.append(parsed.long_description)

    # Args section
    if parsed.params:
        md_lines.append("\n**Args:**")
        for p in parsed.params:
            type_suffix = f" ({p.type_name})" if p.type_name else ""
            default_suffix = f"(default: `{p.default}`)" if p.default else ""
            md_lines.append(f"- **{p.arg_name}**{type_suffix}: {p.description}{default_suffix}")

    # Returns section
    if parsed.returns:
        md_lines.append("\n**Returns:**")
        r = parsed.returns
        if r.type_name:
            md_lines.append(f"**{r.type_name}**")
        if r.description:
            md_lines.append(r.description)

    # Combine tags and description
    full_md = tags_str + "\n\n" + "\n".join(md_lines) if tags_str else "\n".join(md_lines)

    # Display in a panel with markdown rendering
    console.print(
        Panel(
            Markdown(full_md),
            title=f"[bold cyan]{name}[/bold cyan]",
            title_align="left",
            border_style="cyan",
            padding=(1, 1, 1, 1),
        )
    )
    console.print()  # Blank line after each tool
