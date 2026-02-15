"""
Default MCP server instance for uiautomator2-mcp-server.

This file provides a default FastMCP server instance with common configuration
for deployment to Prefect Horizon (https://horizon.prefect.io) or other MCP hosts.

Usage with Horizon:
    Server entrypoint: u2mcp/default.py:mcp
"""

from .mcp import make_mcp

# Create the MCP instance for deployment
mcp = make_mcp(
    token=None,  # Horizon will handle authentication
    include_tags=None,  # Include all tools
    exclude_tags=None,  # Don't exclude any tools
    print_tags=False,  # Don't print tags in server mode
    fix_empty_responses=True,  # Enable middleware for better LLM compatibility
    xpath_timeout=20.0,  # Default XPath timeout
)
