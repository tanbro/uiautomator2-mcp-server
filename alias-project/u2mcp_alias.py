# u2mcp - Alias package for uiautomator2-mcp-server
#
# This is an alias package. The actual implementation is in uiautomator2-mcp-server.
# When you install 'u2mcp', it installs 'uiautomator2-mcp-server' as a dependency.

from importlib import import_module

__all__ = ["main"]


def main() -> None:
    """Entry point that forwards to uiautomator2-mcp-server.

    This function is the CLI entry point for the 'u2mcp' alias package.
    It imports and runs the main function from the real uiautomator2-mcp-server package.
    """
    # Import and run the main function from uiautomator2-mcp-server
    # Using import_module to avoid potential namespace issues
    main_module = import_module("u2mcp.__main__")
    main_module.main()
