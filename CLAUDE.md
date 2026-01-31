# uiautomator2-mcp-server

An MCP (Model Context Protocol) server that provides tools for controlling Android devices using uiautomator2.

## Project Overview

This project exposes Android device automation capabilities as MCP tools. It uses:
- **fastmcp** for MCP server implementation
- **uiautomator2** for Android device control
- **anyio** for async operations
- **Pillow** for image handling

## Project Structure

```
src/u2mcp/
├── __init__.py          # Package init, exports version info
├── __main__.py          # Entry point for CLI commands
├── version.py           # Version info module
├── mcp.py               # MCP server factory and configuration
├── background.py        # Background task management
├── health.py            # ADB availability check
├── helpers.py           # Helper functions for CLI output (tags, tools, info)
└── tools/
    ├── __init__.py      # Tools registry
    ├── device.py        # Device management tools
    ├── action.py        # Touch/gesture tools
    ├── app.py           # App management tools
    ├── clipboard.py     # Clipboard read/write tools
    ├── element.py       # Element/UI interaction tools
    ├── input.py         # Text input and keyboard tools
    ├── misc.py          # Miscellaneous tools
    └── scrcpy.py        # Screen mirroring (scrcpy integration)

tests/
├── conftest.py          # Pytest configuration and fixtures
├── unit/                # Fast unit tests
└── integration/         # Integration tests requiring real devices
```

## Development Setup

```bash
# Install dependencies (uses uv lock file)
uv sync --dev
```

Activate virtual environment

```bash
source .venv/bin/activate  # Linux/macOS
```

or Windows:

```powershell
.venv\Scripts\activate
```

## Running Tests

```bash
# Run all tests
pytest

# Run only unit tests (fast, no device required)
pytest -m unit

# Run integration tests (requires Android device)
pytest -m integration

# Run with coverage
pytest --cov=src/u2mcp --cov-report=html
```

## Test Markers

- `unit` - Unit tests (fast, no external dependencies)
- `integration` - Integration tests (may require external services)
- `slow` - Slow running tests
- `device` - Tests that require actual Android device

## Code Style

- Python >= 3.11
- Type hints required for all function signatures
- Use `from __future__ import annotations` for deferred evaluation
- Use `typing_extensions` for Python < 3.12 compatibility
- Ruff for linting
- mypy for type checking

## CLI Entry Points

The server can be invoked using any of these commands (they are aliases):
- `u2mcp` - Short form (primary)
- `uiautomator2-mcp` - Full form
- `uiautomator2-mcp-server` - Descriptive form

## MCP Tools

All tools are decorated with `@mcp.tool()` and accept a `serial` parameter to identify the target device.

### Device Management
- `device_list` - List connected devices
- `init` - Install uiautomator2 resources to device (REQUIRED before other operations)
- `connect`/`disconnect` - Manage device connections
- `info` - Get device information
- `window_size` - Get screen dimensions
- `screenshot` - Capture screen
- `dump_hierarchy` - Get UI hierarchy XML
- `purge` - Purge all resources (minicap, minitouch, uiautomator) from device
- `shell_command` - Run arbitrary shell commands on device with timeout

### Action Tools
- `click`/`long_click`/`double_click` - Touch actions
- `swipe`/`swipe_points`/`drag` - Gesture actions
- `press_key` - Press a physical key (e.g., HOME, BACK, ENTER)
- `screen_on` - Turn the device screen on
- `screen_off` - Turn the device screen off

### Input Tools
- `send_text` - Type text into the focused input field
- `clear_text` - Clear text in the focused input field
- `hide_keyboard` - Hide the on-screen keyboard

### App Management
- `app_install`/`app_uninstall` - Package management
- `app_uninstall_all` - Uninstall all third-party applications
- `app_start`/`app_stop` - App lifecycle
- `app_stop_all` - Stop all running applications
- `app_wait` - Wait for an app to start (with timeout)
- `app_clear` - Clear app data and cache
- `app_info`/`app_list` - App information
- `app_current` - Get the current foreground app information
- `app_list_running` - List all currently running applications
- `app_auto_grant_permissions` - Auto-grant all permissions to an app

### Clipboard Tools
- `read_clipboard` - Read clipboard content from device
- `write_clipboard` - Write text to device clipboard

### Element Tools
- `activity_wait` - Wait for a specific activity to appear (with timeout)
- `element_wait` - Wait for an element to appear
- `element_wait_gone` - Wait for an element to disappear
- `element_click` - Click on an element found by XPath (with wait)
- `element_click_nowait` - Click on an element without waiting
- `element_click_until_gone` - Click until element disappears
- `element_long_click` - Long click on an element
- `element_screenshot` - Take a screenshot of a specific element
- `element_get_text` - Get text from an element
- `element_set_text` - Set text on an element
- `element_bounds` - Get the bounding box coordinates of an element
- `element_swipe` - Swipe within an element
- `element_scroll` - Scroll within a scrollable container
- `element_scroll_to` - Scroll to a specific element or position

### Screen Mirroring
- `start_scrcpy` - Start scrcpy screen mirroring (requires scrcpy installed)
- `stop_scrcpy` - Stop scrcpy screen mirroring

### Miscellaneous Tools
- `delay` - Add a simple delay/sleep in seconds

## Key Implementation Details

### Device Connection Pool
- `_devices` dict caches device connections with per-device locks
- `get_device()` async context manager provides thread-safe device access
- Global `_global_device_connection_lock` protects connection cache

### Background Tasks
- `background.py` manages background task group via `set_monitor_task_group()`
- Used for scrcpy process monitoring

### Health Check
- `health.py` provides ADB availability check at server startup
- Shows ADB server version and connected devices
- Provides platform-specific installation instructions when ADB is not found
- Can be bypassed with `--skip-adb-check` CLI flag

### CLI Helpers
- `helpers.py` provides functions for displaying tools, tags, and help information
- Uses `docstring_parser` to parse Google-style docstrings
- Uses Rich for formatted terminal output (tables, panels, markdown)
- Functions:
  - `print_tags()` - Display tags with optional filtering
  - `print_tool_help()` - Display tool list or detailed tool info
  - Supports wildcard patterns for filtering (`*` and `?`)

## Adding New Tools

1. Create tool function in appropriate `tools/*.py` module
2. Decorate with `@mcp.tool("tool_name", tags={"category:subcategory"})`
3. Use `get_device(serial)` context manager for device access
4. Run CPU-bound operations in `to_thread.run_sync()`
5. Use FastMCP context for user feedback: `get_context().info()`
6. Write docstrings in **Google style format** for proper parsing by `info` command:

```python
@mcp.tool("my_tool", tags={"device:info"})
async def my_tool(serial: str, param: str) -> dict[str, Any]:
    """Brief one-line description.

    Longer description if needed (optional).

    Args:
        serial: Android device serial number.
        param: Description of the parameter.

    Returns:
        dict[str, Any]: Description of return value structure.
    """
    async with get_device(serial) as device:
        result = await to_thread.run_sync(lambda: device.some_method(param))
    return {"result": result}
```

### Tool Tags

All tools should be tagged using the `category:subcategory` format for selective filtering:

| Category | Subcategories |
|----------|---------------|
| `device` | `manage`, `info`, `capture`, `shell` |
| `action` | `touch`, `gesture`, `key`, `screen` |
| `app` | `manage`, `lifecycle`, `info`, `config` |
| `element` | `wait`, `interact`, `query`, `modify`, `gesture`, `capture` |
| `input` | `text`, `keyboard` |
| `clipboard` | `read`, `write` |
| `screen` | `mirror`, `capture` |
| `util` | `delay` |

Example:
```python
@mcp.tool("my_tool", tags={"device:info"})
async def my_tool(serial: str, param: str) -> dict[str, Any]:
    async with get_device(serial) as device:
        result = await to_thread.run_sync(lambda: device.some_method(param))
    return {"result": result}
```

## Common Commands

```bash
# Run the server (alternative entry points: uiautomator2-mcp, uiautomator2-mcp-server)
u2mcp --host 0.0.0.0 --port 8000 http

# Run in stdio mode
u2mcp stdio

# Run with auth token
u2mcp --token MY_TOKEN http

# Run with disabled token verification (HTTP only)
u2mcp --no-token http

# Enable JSON response format (HTTP only)
u2mcp --json-response http

# Skip ADB availability check at startup
u2mcp --skip-adb-check http

# CLI Utility Commands
u2mcp tools              # List all available tools
u2mcp info screenshot    # Show detailed info for a tool
u2mcp info "device:*"    # Show info for all device tools (supports wildcards)
u2mcp tags               # List all available tool tags
u2mcp version            # Show version information

# Tool filtering - only expose specific tools
u2mcp --include-tags device:manage,action:touch stdio
u2mcp --exclude-tags screen:mirror,device:shell stdio

# Lint
ruff check src/

# Format
ruff format src/

# Type check
mypy src/
```

## Environment Variables

- `ADBUTILS_ADB_PATH` - Custom path to ADB executable
- `SCRCPY` - Custom path to scrcpy executable for screen mirroring

## Troubleshooting

### ADB Not Found
If you get "ADB not found" errors at startup:

1. **Install ADB (Android Platform Tools):**
   - **macOS:** `brew install android-platform-tools`
   - **Linux (Debian/Ubuntu):** `sudo apt install adb`
   - **Linux (Fedora/RHEL):** `sudo yum install android-tools`
   - **Windows:** Download from https://developer.android.com/tools/releases/platform-tools or use `winget install Google.PlatformTools`

2. **Start ADB server:**
   ```bash
   adb start-server
   ```

3. **Set custom ADB path (if needed):**
   - **Linux/macOS:** `export ADBUTILS_ADB_PATH=/path/to/adb`
   - **Windows (CMD):** `set ADBUTILS_ADB_PATH=C:\path\to\adb.exe`
   - **Windows (PowerShell):** `$env:ADBUTILS_ADB_PATH='C:\path\to\adb.exe'`

4. **Bypass the check (not recommended):**
   ```bash
   u2mcp --skip-adb-check http
   ```

### Device Connection Issues
- Ensure USB debugging is enabled on the device
- Check device is authorized: `adb devices` (should show device, not "unauthorized")
- Run the `init` tool before other operations
- Try reconnecting: `adb kill-server && adb start-server`

### Device Not Responding
- Check if device screen is on
- Verify uiautomator2 is installed: run `init` tool
- Restart ADB: `adb kill-server && adb start-server`

### Scrcpy Issues
If `start_scrcpy` fails to start:

1. **Install scrcpy:**
   - **macOS:** `brew install scrcpy`
   - **Linux (Debian/Ubuntu):** `sudo apt install scrcpy`
   - **Windows:** Download from https://github.com/Genymobile/scrcpy/releases

2. **Set custom scrcpy path (if needed):**
   - **Linux/macOS:** `export SCRCPY=/path/to/scrcpy`
   - **Windows (CMD):** `set SCRCPY=C:\path\to\scrcpy.exe`
   - **Windows (PowerShell):** `$env:SCRCPY='C:\path\to\scrcpy.exe'`
