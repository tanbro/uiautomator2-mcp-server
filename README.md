# uiautomator2-mcp-server

[![PyPI](https://img.shields.io/pypi/v/uiautomator2-mcp-server)](https://pypi.org/project/uiautomator2-mcp-server/)
[![CI](https://github.com/tanbro/uiautomator2-mcp-server/actions/workflows/ci.yml/badge.svg)](https://github.com/tanbro/uiautomator2-mcp-server/actions/workflows/ci.yml)
[![Language](https://img.shields.io/badge/lang-English-blue)](README.md)
[![Language](https://img.shields.io/badge/lang-中文-red)](README.zh-CN.md)

An [MCP](https://modelcontextprotocol.io/) server that provides tools for controlling Android devices using [uiautomator2](https://github.com/openatx/uiautomator2).

> Use AI to automate your Android device: take screenshots, tap/swipe, manage apps, send text, and more.

## Prerequisites

- [Python][] 3.11+
- `adb` in your PATH (install via [Android SDK Platform Tools](https://developer.android.com/tools/releases/platform-tools))
- Android device with **USB debugging enabled**

## Installation

### Standalone Installation

Install the server globally on your system by [pip][], [uv][](recommended), or [pipx][]:

```bash
# Using uv (recommended)
uv tool install uiautomator2-mcp-server

# Or using pipx
pipx install uiautomator2-mcp-server

# Or using pip
pip install uiautomator2-mcp-server
```

### Running Modes

The MCP server can run in two modes:

#### STDIO Mode (for local MCP clients)

```bash
u2mcp stdio
```

This mode communicates via standard input/output and is typically used by MCP clients that spawn the server process directly.

#### HTTP Mode (for remote/network access)

```bash
# Basic HTTP server
u2mcp --host 0.0.0.0 --port 8000 --no-token http

# With authentication token
u2mcp --host 0.0.0.0 --port 8000 --token YOUR_SECRET_TOKEN http
```

The server will listen on `http://localhost:8000/mcp` (or your specified host/port).

## Testing and Debugging

### Using MCP Inspector

[MCP Inspector](https://github.com/modelcontextprotocol/inspector) is a command-line tool for testing and debugging MCP servers without requiring an AI client.

```bash
# Install MCP Inspector
npm install -g @modelcontextprotocol/inspector

# Inspect the server in STDIO mode
npx @modelcontextprotocol/inspector u2mcp stdio

# Or inspect the server in HTTP mode
# First start the server: u2mcp --host 0.0.0.0 --port 8000 http
# Then run inspector with the URL
npx @modelcontextprotocol/inspector http://localhost:8000/mcp
```

The inspector will display:
- Available tools and their parameters
- Server resources and prompts
- Real-time tool execution results
- Request/response logs

### Using Postman or cURL

You can test the HTTP endpoint using any HTTP client like Postman or cURL.

#### Using cURL

```bash
# 1. Start the server first
u2mcp --host 0.0.0.0 --port 8000 http

# 2. In another terminal, send MCP requests
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list"
  }'

# Call a tool (e.g., list devices)
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "device_list",
      "arguments": {}
    }
  }'
```

#### Using Postman

1. Start the server: `u2mcp --host 0.0.0.0 --port 8000 http`
2. Create a new POST request to `http://localhost:8000/mcp`
3. Set headers:
   - `Content-Type: application/json`
4. Send JSON-RPC 2.0 requests in the body:

Example request body for listing tools:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list"
}
```

Example request body for calling a tool:
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "device_list",
    "arguments": {}
  }
}
```

## MCP Client Configuration

This MCP server can be used with any MCP-compatible client. Below are configuration instructions for popular clients.

### Claude Desktop

Add to your Claude Desktop config file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "android": {
      "command": "uvx",
      "args": ["uiautomator2-mcp-server", "stdio"]
    }
  }
}
```

If you installed the package globally, you can also use:

```json
{
  "mcpServers": {
    "android": {
      "command": "u2mcp",
      "args": ["stdio"]
    }
  }
}
```

### Cursor

Cursor is an AI-powered code editor with native MCP support.

1. Open Cursor Settings (Cmd/Ctrl + ,)
2. Navigate to **MCP Servers**
3. Add a new server:

```json
{
  "mcpServers": {
    "android": {
      "command": "u2mcp",
      "args": ["stdio"]
    }
  }
}
```

### Cherry Studio

[Cherry Studio](https://cherry-ai.com/) is a cross-platform AI desktop client with full MCP support. Ideal for Android device automation tasks.

1. Download and install [Cherry Studio](https://github.com/CherryHQ/cherry-studio)
2. Open Settings and navigate to **MCP Servers**
3. Click **Add Server** and configure:

**Option A: Using uvx (recommended)**
```
Command: uvx
Arguments: uiautomator2-mcp-server stdio
```

**Option B: Using installed u2mcp command**
```
Command: u2mcp
Arguments: stdio
```

**Option C: HTTP Mode**
First start the server:
```bash
u2mcp --host 0.0.0.0 --port 8000 --no-token http
```

Then in Cherry Studio, select HTTP mode and enter:
```
URL: http://localhost:8000/mcp
```

For detailed MCP configuration in Cherry Studio, see the [official documentation](https://docs.cherry-ai.com/docs/en-us/advanced-basic/mcp/config).

### ChatMCP

[ChatMCP](https://github.com/daodao97/chatmcp) is an open-source AI chat client implementing the MCP protocol. Supports multiple LLM providers (OpenAI, Claude, Ollama).

1. Download and install [ChatMCP](https://github.com/daodao97/chatmcp)
2. Open Settings and navigate to **MCP Servers**
3. Add a new server:

**Using uvx (recommended)**
```
Command: uvx
Arguments: uiautomator2-mcp-server stdio
```

**Using installed u2mcp command**
```
Command: u2mcp
Arguments: stdio
```

**HTTP Mode**
First start the server:
```bash
u2mcp --host 0.0.0.0 --port 8000 --no-token http
```

Then in ChatMCP, select HTTP mode and enter:
```
URL: http://localhost:8000/mcp
```

### Cline

Cline is an AI coding assistant extension that supports MCP.

1. Open Cline settings in your IDE
2. Navigate to **MCP Servers** section
3. Add the server configuration:

```json
{
  "android": {
    "command": "u2mcp",
      "args": ["stdio"]
  }
}
```

### Continue

Continue is an AI pair programmer extension for VS Code and JetBrains.

1. Install the [Continue extension](https://marketplace.visualstudio.com/items?itemName=Continue.continue)
2. Open Continue settings
3. Add to your MCP servers configuration:

```json
{
  "mcpServers": {
    "android": {
      "command": "u2mcp",
      "args": ["stdio"]
    }
  }
}
```

### HTTP Mode Configuration

For clients that support HTTP connections (or for remote access), start the server first:

```bash
u2mcp --host 0.0.0.0 --port 8000 --no-token http
```

Then configure your client to connect to `http://localhost:8000/mcp`.

**Note:** Check your client's documentation for HTTP MCP server configuration, as the setup varies by client.

### Other MCP Clients

The server follows the [Model Context Protocol](https://modelcontextprotocol.io/) specification and can be used with any MCP-compatible client, including:

- **Windsurf** - Development environment with MCP support
- **Zed** - Code editor with MCP capabilities
- **LibreChat** - Chat interface supporting MCP
- **Chainlit** - Platform for building AI applications

Refer to your client's documentation for specific configuration details.

## Quick Start

1. **Connect your Android device** via USB with USB debugging enabled
2. **Initialize the device** (required first time):

   > "Initialize my Android device"

3. **Start automating**:

   > "Take a screenshot"
   > "Tap at coordinates 500, 1000"
   > "Swipe up"
   > "Open YouTube app"

## Available Tools

### Device
| Tool | Description |
|------|-------------|
| `device_list` | List connected devices |
| `init` | Install required resources to device (**run first**) |
| `info` | Get device information |
| `screenshot` | Take screenshot |
| `dump_hierarchy` | Get UI hierarchy XML |

### Actions
| Tool | Description |
|------|-------------|
| `click` | Tap at coordinates |
| `long_click` | Long press at coordinates |
| `double_click` | Double tap at coordinates |
| `swipe` | Swipe from point A to B |
| `swipe_points` | Swipe through multiple points |
| `drag` | Drag from point A to B |
| `press_key` | Press a key (home, back, etc.) |
| `send_text` | Type text |
| `clear_text` | Clear text field |

### Apps
| Tool | Description |
|------|-------------|
| `app_start` | Launch an app |
| `app_stop` | Stop an app |
| `app_list` | List installed apps |
| `app_current` | Get current foreground app |
| `app_install` | Install APK |
| `app_uninstall` | Uninstall app |
| `app_info` | Get app info |
| `app_clear` | Clear app data |

## Example Usage

```txt
You: Take a screenshot
Claude: [Uses screenshot tool, displays image]

You: What apps are installed?
Claude: [Lists installed apps using app_list]

You: Open the YouTube app
Claude: [Uses app_start with package name]

You: Search for "cats"
Claude: [Uses click to tap search bar, then send_text to type "cats"]

You: Scroll down
Claude: [Uses swipe to scroll down]
```

## License

GPL-3.0

------

[python]: https://www.python.org/ "Python is a programming language that lets you work quickly and integrate systems more effectively."
[pip]: https://pip.pypa.io/ "The most popular tool for installing Python packages, and the one included with modern versions of Python."
[pipx]: https://pipx.pypa.io/ "pipx is a tool to install and run Python command-line applications without causing dependency conflicts with other packages installed on the system."
[uv]: https://docs.astral.sh/uv/ "An extremely fast Python package and project manager"
