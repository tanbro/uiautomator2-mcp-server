# u2mcp

**MCP server for Android device automation using uiautomator2**

This is an alias package for [`uiautomator2-mcp-server`](https://github.com/tanbro/uiautomator2-mcp-server).

## Installation

```bash
# Install the alias (installs uiautomator2-mcp-server as dependency)
pip install u2mcp

# Or run directly without installation
uvx u2mcp stdio
```

## Quick Start

After installation, the `u2mcp` command is available:

```bash
# Run in STDIO mode
u2mcp stdio

# Run in HTTP mode
u2mcp http -H 0.0.0.0 -p 8000

# List available tools
u2mcp tools

# Show tool information
u2mcp info screenshot
```

## Why Two Package Names?

- **`uiautomator2-mcp-server`** - The main package (descriptive name)
- **`u2mcp`** - Convenient alias (short name)

In v1.0.0, `u2mcp` will become the primary package name.

## Documentation

See [uiautomator2-mcp-server Documentation](https://github.com/tanbro/uiautomator2-mcp-server) for full details.

## License

Apache-2.0
