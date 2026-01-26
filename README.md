# uiautomator2-mcp-server

[![PyPI](https://img.shields.io/pypi/v/uiautomator2-mcp-server)](https://pypi.org/project/uiautomator2-mcp-server/)
[![CI](https://github.com/tanbro/uiautomator2-mcp-server/actions/workflows/ci.yml/badge.svg)](https://github.com/tanbro/uiautomator2-mcp-server/actions/workflows/ci.yml)

An [MCP](https://modelcontextprotocol.io/) server that provides tools for controlling Android devices using [uiautomator2](https://github.com/openatx/uiautomator2).

> Use AI to automate your Android device: take screenshots, tap/swipe, manage apps, send text, and more.

## Prerequisites

- Python 3.11+
- `adb` in your PATH (install via [Android SDK Platform Tools](https://developer.android.com/tools/releases/platform-tools))
- Android device with **USB debugging enabled**

## Installation

### Claude Desktop (Recommended)

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

Alternatively, install globally first:

```bash
# Using uv (recommended)
uv tool install uiautomator2-mcp-server

# Or using pipx
pipx install uiautomator2-mcp-server

# Or using pip
pip install uiautomator2-mcp-server
```

Then use `u2mcp` as the command:

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

### HTTP Mode (for remote/network access)

```bash
u2mcp --host 0.0.0.0 --port 8000 http
```

With authentication token:

```bash
u2mcp --host 0.0.0.0 --port 8000 --token YOUR_SECRET_TOKEN http
```

Then configure your MCP client to connect to `http://localhost:8000/mcp`.

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
