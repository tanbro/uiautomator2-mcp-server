# uiautomator2-mcp-server

[![GitHub Tag](https://img.shields.io/github/v/tag/tanbro/uiautomator2-mcp-server)](https://github.com/tanbro/uiautomator2-mcp-server)
[![PyPI - Version](https://img.shields.io/pypi/v/uiautomator2-mcp-server)](https://pypi.org/project/uiautomator2-mcp-server/)

A MCP (Model Context Protocol) server that provides tools for controlling and interacting with Android devices using uiautomator2. This server allows you to perform various operations on Android devices such as connecting to devices, taking screenshots, getting device information, accessing UI hierarchy, tap on screens, and more.

## Features

- **Device Management**: List connected devices, initialize devices, connect/disconnect from devices
- **Screen Operations**: Take screenshots, get device window size, dump UI hierarchy
- **Touch Actions**: Click, long click, double click at specific coordinates
- **Gesture Controls**: Swipe, swipe through multiple points, drag operations
- **System Controls**: Screen on/off, key presses
- **App Management**: Install, uninstall, start, stop, clear, and manage Android applications
- **Text Operations**: Send text input, clear text fields

## Requirements

- Python >= 3.11
- adb executable in your PATH
- Android device connected in debug mode

## Installation

```bash
# Install the package
pip install uiautomator2-mcp-server
```

## Usage

### Running the Server

The server can be run in different transport modes:

```bash
# Run in streamable HTTP mode
u2mcp --host 0.0.0.0 --port 8000 --no-token http

# Run in stdio mode
u2mcp stdio
```

### Using the Tools

Connect it to any tool that supports MCP protocol.

## Available Tools

### Device Management
- `device_list`: Get list of connected devices
- `init`: Install essential resources to device
- `connect`, `disconnect`, `disconnect_all`: Manage device connections
- `info`: Get device information
- `window_size`: Get device window size
- `screenshot`: Take device screenshot
- `dump_hierarchy`: Get UI hierarchy of device

### Action Tools
- `click`: Click at specific coordinates
- `long_click`: Long click at specific coordinates
- `double_click`: Double click at specific coordinates
- `swipe`: Swipe from one point to another
- `swipe_points`: Swipe through multiple points
- `drag`: Drag from one point to another
- `press_key`: Press device key
- `send_text`: Send text to device
- `clear_text`: Clear text input
- `screen_on`/`screen_off`: Control screen state

### App Management
- `app_install`: Install an app
- `app_uninstall`: Uninstall an app
- `app_uninstall_all`: Uninstall all apps
- `app_start`: Start an app
- `app_stop`: Stop an app
- `app_stop_all`: Stop all apps
- `app_clear`: Clear app data
- `app_info`: Get app information
- `app_current`: Get current app
- `app_list`: List installed apps
- `app_list_running`: List running apps
- `app_auto_grant_permissions`: Auto grant permissions

## License

This project is licensed under the GNU General Public License v3.0 (GPL-3.0).
