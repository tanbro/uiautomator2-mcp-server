# u2mcp - Alias package for uiautomator2-mcp-server
#
# This is an alias package. The actual implementation is in uiautomator2-mcp-server.
# When you install 'u2mcp', it installs 'uiautomator2-mcp-server' as a dependency.
#
# This file should be placed at u2mcp/__init__.py when building the alias package.

# Import version from the real package
try:
    from u2mcp import __version__
except ImportError:
    # Fallback if uiautomator2-mcp-server is not installed yet
    __version__ = "0.3.0"

__all__ = ["__version__"]
