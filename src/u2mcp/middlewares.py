"""Middleware to fix empty responses for Zhipu AI compatibility."""

from __future__ import annotations

from fastmcp.server.middleware.middleware import CallNext, Middleware, MiddlewareContext
from fastmcp.tools.tool import ToolResult
from mcp.types import CallToolRequestParams, TextContent


class EmptyResponseMiddleware(Middleware):
    """Middleware that converts empty tool responses to non-empty values.

    This is needed for compatibility with Zhipu AI model service, which doesn't
    handle empty responses (content: []) correctly.

    When enabled, this middleware will convert empty content to "" (empty string).
    """

    async def on_call_tool(
        self,
        context: MiddlewareContext[CallToolRequestParams],
        call_next: CallNext[CallToolRequestParams, ToolResult],
    ) -> ToolResult:
        """Intercept tool calls and fix empty responses."""
        result = await call_next(context)

        # Convert empty content to empty string for Zhipu compatibility
        if isinstance(result, ToolResult):
            if not result.content:
                # Empty content - return empty string
                result.content = [TextContent(type="text", text="")]
            elif (
                isinstance(result.content, list)
                and len(result.content) == 1
                and isinstance(result.content[0], dict)
                and not result.content[0].get("text")
            ):
                # Missing/empty text - set to empty string
                result.content[0]["text"] = ""

        return result
