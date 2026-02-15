"""
FastMCP server entry point for Prefect Horizon deployment.

This is the standard entry point expected by FastMCP deployment platforms.
It creates and exports the MCP server instance with default configuration.

Usage:
    Server entrypoint: server.py:mcp
"""

from u2mcp.default import mcp

__all__ = ["mcp"]
