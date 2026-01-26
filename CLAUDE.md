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
├── _version.py          # Auto-generated version info (SCM)
├── mcp.py               # MCP server factory and configuration
├── background.py        # Background task management
└── tools/
    ├── __init__.py      # Tools registry
    ├── device.py        # Device management tools
    ├── action.py        # Touch/gesture tools
    ├── app.py           # App management tools
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

# Activate virtual environment
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate     # Windows
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

### Action Tools
- `click`/`long_click`/`double_click` - Touch actions
- `swipe`/`swipe_points`/`drag` - Gesture actions

### App Management
- `app_install`/`app_uninstall` - Package management
- `app_start`/`app_stop` - App lifecycle
- `app_info`/`app_list` - App information

## Key Implementation Details

### Device Connection Pool
- `_devices` dict caches device connections with per-device locks
- `get_device()` async context manager provides thread-safe device access
- Global `_global_device_connection_lock` protects connection cache

### Background Tasks
- `background.py` manages background task group via `set_monitor_task_group()`
- Used for scrcpy process monitoring

## Adding New Tools

1. Create tool function in appropriate `tools/*.py` module
2. Decorate with `@mcp.tool("tool_name")`
3. Use `get_device(serial)` context manager for device access
4. Run CPU-bound operations in `to_thread.run_sync()`
5. Use FastMCP context for user feedback: `get_context().info()`

Example:
```python
@mcp.tool("my_tool")
async def my_tool(serial: str, param: str) -> dict[str, Any]:
    async with get_device(serial) as device:
        result = await to_thread.run_sync(lambda: device.some_method(param))
    return {"result": result}
```

## Common Commands

```bash
# Run the server
u2mcp --host 0.0.0.0 --port 8000 http

# Run in stdio mode
u2mcp stdio

# Run with auth token
u2mcp --token MY_TOKEN http

# Lint
ruff check src/

# Format
ruff format src/

# Type check
mypy src/
```
