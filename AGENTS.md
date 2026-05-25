# uiautomator2-mcp-server

An MCP (Model Context Protocol) server that provides tools for controlling Android devices using uiautomator2.

## Project Overview

This project exposes Android device automation capabilities as MCP tools. It uses:
- **fastmcp** for MCP server implementation
- **cyclopts** for CLI argument parsing (via fastmcp dependency)
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
├── health.py            # ADB availability check and doctor command
├── helpers.py           # Helper functions for CLI output (tags, tools, info)
├── middlewares.py       # MCP middlewares for request/response handling
└── tools/
    ├── __init__.py      # Tools registry
    ├── action.py        # Touch/gesture tools (click, swipe, drag, etc.)
    ├── app.py           # App management tools
    ├── clipboard.py     # Clipboard read/write tools
    ├── delay.py         # Delay utility
    ├── device.py        # Device management tools
    ├── gesture.py       # Edge swipe and multitouch gestures
    ├── input.py         # Text input and keyboard tools
    ├── scrcpy.py        # Screen mirroring (scrcpy integration)
    ├── screenrecord.py  # Screen recording tools
    ├── system.py        # System controls (orientation, notification, unlock)
    ├── toast.py         # Toast message utilities
    └── xpath.py         # XPath-based element tools (primary)

.skills/                  # AI-driven testing skills
├── android-ui-test/
│   ├── SKILL.md         # Skill definition
│   ├── README.md        # Skill documentation
│   ├── examples/        # Usage examples
│   └── references/      # Technical specifications

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
- Use `Annotated[type, Parameter(...)]` for CLI parameters with custom names
- Ruff for linting
- mypy for type checking with `types-lxml` and `types-retry` for proper type coverage

## CLI Entry Points

The server can be invoked using any of these commands (they are aliases):
- `u2mcp` - Short form (primary)
- `uiautomator2-mcp` - Full form
- `uiautomator2-mcp-server` - Descriptive form

## MCP Tools

All tools are decorated with `@mcp.tool()` and accept a `serial` parameter to identify the target device.

Tools are organized into modules:
- **action.py** - Coordinate-based touch/gestures (click, swipe, drag)
- **xpath.py** - XPath-based element location and interaction (primary, LLM-optimized)
- **device.py** - Device management and screen capture
- **app.py** - Application lifecycle and management
- **input.py** - Text input and keyboard control
- **gesture.py** - Edge swipes and multitouch gestures
- **system.py** - System controls (orientation, notification, unlock)
- **screenrecord.py** - Screen recording
- **scrcpy.py** - Screen mirroring
- **clipboard.py** - Clipboard read/write
- **delay.py** - Delay utility
- **toast.py** - Toast messages

Use `u2mcp tools` to list all available tools.

## Tool Function Design Principles

**Core Philosophy: Naming, types, and docstrings are for LLM consumption.**

The audience for tool function signatures and documentation is the LLM, not human developers. Design for LLM understanding.

### 1. Mandatory Type Annotations

All parameters and return values MUST have explicit type annotations.

### 2. Minimize Type Complexity

Keep parameter and return types simple for LLM understanding.

**Avoid:**
- `Optional[T]` - Use separate required parameters or provide defaults
- `Dict[str, Any]` - Use specific dataclasses or named tuples
- `List[T]` - Use fixed-size tuples or separate parameters
- `Union[T1, T2]` - Use separate functions or overload

**Prefer:**
- `str`, `int`, `float`, `bool`
- `tuple[int, int, int, int]` for coordinates
- Literal types like `Literal["left", "right", "up", "down"]`

### 3. No Redundant Return Type Annotations

For functions with no meaningful return value, do NOT add `-> None` or include a `Returns:` section.

```python
# Good
@mcp.tool("screen_on", tags={"action:screen"})
async def screen_on(serial: str):
    """Turn screen on.

    Args:
        serial: Android device serial number.
    """
    ...

# Bad - redundant None
async def screen_on(serial: str) -> None:
    """Turn screen on.

    Args:
        serial: Android device serial number.

    Returns:
        None: Nothing.
    """
```

### 4. Google-Style Docstrings with Types in Descriptions

Docstrings MUST use Google Python style format. Include types in parameter descriptions.

```python
@mcp.tool("click", tags={"action:touch"})
async def click(serial: str, x: int, y: int) -> bool:
    """Click at specific coordinates.

    Args:
        serial: Android device serial number.
        x: X coordinate in pixels.
        y: Y coordinate in pixels.

    Returns:
        bool: True if click successful, False otherwise.
    """
```

### 5. No Examples in Tool Docstrings

Do NOT include usage examples in tool function docstrings unless absolutely critical for LLM understanding. Examples bloat the documentation and confuse the LLM.

## Key Implementation Details

### Device Connection Pool
- `_devices` dict caches device connections with per-device locks
- `get_device()` async context manager provides thread-safe device access
- Global `_global_device_connection_lock` protects connection cache

### Background Tasks
- `background.py` manages background task group via `set_background_task_group()`
- Used for scrcpy process monitoring

### Health Check
- `health.py` provides ADB availability check at server startup
- Shows ADB server version and connected devices
- Provides platform-specific installation instructions when ADB is not found
- Can be bypassed with `--no-check-adb` CLI flag (default: enabled)

### Doctor Command
- `run_doctor()` provides comprehensive diagnostics for troubleshooting
- Checks environment (Python version, platform, executable path)
- Validates ADB availability (server version, device count)
- Tests device connectivity (connection status, authorization)
- Verifies uiautomator2 initialization status
- Confirms MCP tool registration
- Checks scrcpy availability (optional)
- Options:
  - `--verbose, -v`: Show detailed diagnostic output
  - `--fix`: Attempt automatic fixes for issues
  - `--category, -c`: Only check specific categories
  - `--exclude`: Exclude specific categories

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
u2mcp http -H 0.0.0.0 -p 8000

# Run in stdio mode
u2mcp stdio

# Run with auth token
u2mcp http -t MY_TOKEN

# Run with disabled token verification (HTTP only)
u2mcp http -n

# Enable JSON response format (HTTP only)
u2mcp http --json-response

# Skip ADB availability check at startup
u2mcp stdio --no-check-adb

# CLI Utility Commands
u2mcp tools              # List all available tools
u2mcp info screenshot    # Show detailed info for a tool
u2mcp info "device:*"    # Show info for all device tools (supports wildcards)
u2mcp tags               # List all available tool tags
u2mcp --version          # Show version information
u2mcp doctor             # Run comprehensive diagnostics
u2mcp doctor -v          # Run diagnostics with verbose output
u2mcp doctor -c device   # Run only device-related checks

# Tool filtering - only expose specific tools (short options available)
u2mcp stdio -i device:manage,action:touch
u2mcp stdio -e screen:mirror,device:shell

# Lint
ruff check src/

# Format
ruff format src/

# Type check
mypy src/
```

### CLI Short Options

| Short | Long | Description |
|-------|------|-------------|
| `-l` | `--log-level` | Set log level |
| `-i` | `--include-tags` | Include tools by tags |
| `-e` | `--exclude-tags` | Exclude tools by tags |
| `-H` | `--host` | Set host address (HTTP mode) |
| `-p` | `--port` | Set port number (HTTP mode) |
| `-t` | `--token` | Set authentication token (HTTP mode) |
| `-n` | `--no-token` | Disable token verification (HTTP mode) |
| `-v` | `--verbose` | Show detailed diagnostic output (doctor command) |
| `-c` | `--category` | Only check specific categories (doctor command) |

## Environment Variables

- `ADBUTILS_ADB_PATH` - Custom path to ADB executable
- `SCRCPY` - Custom path to scrcpy executable for screen mirroring

## AI-Driven UI Testing

This project includes an AI-driven UI testing framework using the `.skills/` system. Skills allow AI to execute comprehensive automated tests using natural language specifications.

### Skill Structure

```
.skills/android-ui-test/
├── SKILL.md                     # Core skill definition (YAML metadata + dual-purpose documentation)
├── README.md                    # Architecture overview and quick start
├── examples/                    # Learning materials
│   └── usage-examples.md        # Detailed usage patterns and examples
├── references/                  # Technical specifications
│   └── test-specification.md    # Complete test specification with TC### test cases
└── scripts/                     # Executable scripts (in project root)
    └── demo-android-test.py     # Demonstration script
```

### Dual-Purpose Design

The `android-ui-test` skill serves two purposes:

1. **Educational Example**: Demonstrates best practices for MCP skill development
2. **Production Testing**: Acts as the project's automated UI test suite for CI/CD

### Running Tests

Simply ask the AI to execute a test:

```
Run the Android UI test suite on my connected device
```

The AI will:
- Auto-detect and connect to the first available device
- Run comprehensive tests covering all device operations
- Provide a detailed test report with pass/fail/skip status

### Test Coverage

| Category    | Tests                                    |
|-------------|------------------------------------------|
| Device      | Connection, info, screenshot, hierarchy, doctor |
| Touch       | Click, long press, double click          |
| Gesture     | Swipe, drag, key press                   |
| App         | List, launch, wait, info, permissions    |
| Element     | Wait, bounds, get text, click, screenshot save |
| Input       | Text input, focused text, keyboard       |
| Clipboard   | Read/write (with known limitations)      |

### Creating Custom Skills

See [`.skills/android-ui-test/`](.skills/android-ui-test/) for a complete reference implementation.

Key components:
- `SKILL.md` - YAML frontmatter with metadata and lightweight description
- `examples/` - Detailed usage patterns for learning
- `references/` - Technical specifications and test cases

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
   u2mcp stdio --no-check-adb
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
