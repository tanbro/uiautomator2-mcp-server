"""Helper functions for u2mcp."""

from __future__ import annotations

from typing import TYPE_CHECKING

from rich.console import Console
from rich.table import Table

if TYPE_CHECKING:
    from .mcp import FastMCP


async def print_tags(instance: FastMCP, console: Console, *, filtered: bool = True):
    """Print tags from an MCP instance.

    Args:
        instance: The MCP instance to get tools from
        console: The Rich console to print to
        filtered: If True, only show tags that match include/exclude filters.
                   If False, show all available tags. Defaults to True.
    """
    tags: dict[str, list[str]] = {}
    include_tags = getattr(instance, "include_tags", None) if filtered else None
    exclude_tags = getattr(instance, "exclude_tags", None) if filtered else None

    for tool in (await instance.get_tools()).values():
        tool_tags = tool.tags or []

        # Skip tools with no tags
        if not tool_tags:
            continue

        # Apply include filter
        if include_tags is not None and not any(tag in include_tags for tag in tool_tags):
            continue

        # Apply exclude filter
        if exclude_tags is not None and any(tag in exclude_tags for tag in tool_tags):
            continue

        for tag in tool_tags:
            # Only include tags that pass the filters
            if include_tags is not None and tag not in include_tags:
                continue
            if exclude_tags is not None and tag in exclude_tags:
                continue

            if tag not in tags:
                tags[tag] = []
            tags[tag].append(tool.name)

    # Sort tags by category
    sorted_tags = sorted(tags.keys())

    # Group by category
    categories: dict[str, list[tuple[str, list[str]]]] = {}
    for tag in sorted_tags:
        if ":" in tag:
            category, subcategory = tag.split(":", 1)
            if category not in categories:
                categories[category] = []
            categories[category].append((subcategory, tags[tag]))
        else:
            # Tags without category (if any)
            if "" not in categories:
                categories[""] = []
            categories[""].append((tag, tags[tag]))

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

    console.print(f"\n[bold]Total: {len(tags)} tags, {sum(len(v) for v in tags.values())} tool-tag assignments[/bold]")
