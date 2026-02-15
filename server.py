"""
FastMCP server entry point for Prefect Horizon deployment.

This is the standard entry point expected by FastMCP deployment platforms.
It creates and exports the MCP server instance with default configuration.

Usage:
    Server entrypoint: server.py:mcp
"""

from u2mcp.mcp import make_mcp

# Create the MCP instance for deployment with default configuration
# Horizon will handle authentication via its own OAuth system
mcp = make_mcp(
    token=None,  # Horizon handles authentication
    include_tags=None,  # Include all tools
    exclude_tags=None,  # Don't exclude any tools
    print_tags=False,  # Don't print tags in server mode
    fix_empty_responses=True,  # Enable middleware for better LLM compatibility
    xpath_timeout=20.0,  # Default XPath timeout
)

__all__ = ["mcp"]
