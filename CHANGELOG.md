# CHANGELOG

## 0.3.2.post1

> 📅 2026-02-16

- ✨ Improved:
    - Update server.json description for better SEO: add keywords `mobile`, `bot`, `RPA`, `testing`, `XPath`


## 0.3.2

> 📅 2026-02-16

- 🐛 Fixed:
    - Fix README MCP name validation tag format from dots to slash (`io.github.tanbro/uiautomator2-mcp-server`)
    - Add missing MCP name validation tag to Chinese README (README.zh-CN.md)
    - Update MANIFEST.in to exclude non-runtime files: `server.json`, `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, `pytest.ini`


## 0.3.1

> 📅 2026-02-16

- 🆕 New:
    - Add GitHub Actions workflow for automatic publishing to Official MCP Registry
    - Use GitHub OIDC authentication for network-restricted environments

- ⚙️ Changed:
    - Add `server.json` for MCP Registry submission with proper format
    - Update README with MCP name validation tag for PyPI verification
    - MCP servers can now be installed with one click from VSCode's MCP gallery

- 🗑️ Removed:
    - Remove `pyproject-u2mcp-alias.toml` and `u2mcp-alias-init.py` (abandoned PyPI alias package approach)
    - Remove `src/u2mcp/default.py` (using standard `server.py` entry point instead)

- 🐛 Fixed:
    - Fix server.json to meet MCP Registry validation requirements:
      - Shorten description to 100 characters (was 157)
      - Fix name format from `io.github.tanbro.uiautomator2-mcp-server` to `io.github.tanbro/uiautomator2-mcp-server`
      - Add `packageArguments` for required `stdio` subcommand


## 0.3.0

> 📅 2026-02-12

- 🆕 New:
    - Add three new XPath query tools:
      - `xpath_exists` - Check if element exists by XPath without waiting
      - `xpath_get_info` - Get complete element information as dict (text, bounds, className, clickable, etc.)
      - `xpath_get_attrib` - Get specific attribute value from element by XPath
    - Add `--xpath-timeout` CLI parameter to control default XPath element lookup timeout (default: 20.0 seconds)

- ⚙️ Changed:
    - Move `activity_wait_appear` from `xpath.py` to `device.py` (it's a device-level operation, not XPath)
    - Apply XPath timeout during device connection for efficiency (once per connection instead of every operation)
    - Simplify XPath tools - remove unnecessary return type annotations from void functions
    - Add `scale=0.6` default parameter to `xpath_swipe` tool

## 0.2.2

> 📅 2026-02-10

- 🆕 New:
    - Add Toast tools for Android Toast message detection and display:
      - `get_toast` - Get the most recent Android Toast message using uiautomator2's built-in toast detection
      - `show_toast` - Display a Toast message on the Android device
      - `reset_toast` - Clear the cached Toast message on the device
    - Add `doctor` command for comprehensive diagnostics with options for verbose output, auto-fix, category filtering, and exclusion
    - Add `save_dump_hierarchy` tool to save UI hierarchy XML to local file
    - Add xpath filter parameter to `dump_hierarchy` tool for filtering XML results

- ⚙️ Changed:
    - Add serval type stubs for comprehensive type coverage
    - Restructure README installation section with dedicated "Installing Enhanced Python Package Managers" subsection
    - Add Toast tool documentation to both English and Chinese README
    - Remove unnecessary `-> None` return type annotations from tool functions
    - Simplify MCP server module docstring for clarity
    - Clarify `init` tool scope: only required for UI and element operations
    - Expand PyPI keywords to align with GitHub topics for better discoverability

- 📚 Docs:
    - Update README structure with clearer package manager installation guidance
    - Add Toast tools to Available Tools section in both English and Chinese README
    - Add GitHub Release badge to README for version visibility

## 0.2.1

> 📅 2026-02-10

- 🆕 New:
    - Add `element_save_screenshot` tool to capture screenshots of specific elements
    - Add `set_focused_text` input tool for direct text input without IME requirements
    - Auto-grant all permissions to installed apps with `app_auto_grant_permissions` tool

- ⚙️ Changed:
    - Improve error handling in element tools with better exception messages
    - Update swipe function parameter documentation
    - Improve Chinese documentation translation and clarity
    - Update README structure with better organization

- 🐛 Fixed:
    - Fix element swipe direction validation to only accept valid directions
    - Correct bounds parameter handling in element tools
    - Improve error handling for element not found scenarios

## 0.2.0

> 📅 2026-02-05

- ⛓️‍💥 Breaking:
    - CLI now requires explicit subcommand (`http`, `stdio`, `tools`, `info`, `tags`, or `version`). Running `u2mcp` without arguments shows help instead of starting server with default stdio transport. Migrate by appending `stdio` to your command: `u2mcp` → `u2mcp stdio`
    - Change project license from MIT to Apache-2.0

- 🆕 New:
    - Add CLI short options: `-l` (log-level), `-i` (include-tags), `-e` (exclude-tags), `-H` (host), `-p` (port), `-t` (token), `-n` (no-token)
    - Add `--show-fastmcp-banner` option to stdio and http commands to control fastmcp banner display
    - Add `save_screenshot` tool to save screenshots to file with format determined by extension
    - Add AI-driven UI testing framework with comprehensive test specification
    - Add Android UI test skill as dual-purpose educational example and production test suite
    - Add CLI utility commands: `u2mcp tools`, `u2mcp info <tool>`, `u2mcp tags`, `u2mcp version`
    - Add tag-based tool filtering with wildcard support (`--include-tags`, `--exclude-tags`)
    - Add `element_bounds` tool to get bounding box coordinates of elements
    - Add clipboard read/write tools: `read_clipboard`, `write_clipboard`
    - Add `hide_keyboard` input tool
    - Add new element interaction tools: `element_get_text`, `element_set_text`
    - Add `purge` device tool to remove all resources from device
    - Add `shell_command` tool to run arbitrary shell commands with timeout
    - Add ADB availability check at startup with `--check-adb/--no-check-adb` option
    - Add `version` CLI option to display version information
    - Add alternative CLI entry points: `uiautomator2-mcp`, `uiautomator2-mcp-server`

- ⚙️ Changed:
    - Refactor CLI with cyclopts subcommands (migrated from typer)
    - Move tag parsing and wildcard expansion logic to mcp module
    - Rename `_version.py` to `version.py`
    - Rename `monitor_task_group` to `background_task_group`
    - Rename internal `tags` variable to `tags_map` for clarity
    - Update `shell_command` to return exit code and output
    - Enhance ADB connectivity check with detailed information and platform-specific guidance

- 🐛 Fixed:
    - Add `serial_optional=None` parameter to argparse.Namespace in the init tool
    - Improve scrcpy error handling for process exit during startup
    - Correct scrcpy tool name and add Windows executable support
    - Fix `element_bounds` tool - `bounds` is a property, not a method
    - Correct help command reference in breaking changes documentation

- 📚 Docs:
    - Add CLAUDE.md with comprehensive project documentation
    - Add CLI utility commands documentation to README
    - Add tool tagging system documentation
    - Add installation guides for uv and pipx
    - Add Chinese translation to README
    - Add code of conduct and contribution guidelines
    - Add ADB troubleshooting guidance
    - Add AI-driven UI testing documentation to README (English and Chinese)

- 🧪 Tests:
    - Enhance u2 device mock with comprehensive functionality
    - Add AI-driven UI testing skill with comprehensive test specification

- 🐎 Chores:
    - Update check-jsonschema version
    - Add .gitignore file for local config
    - Adjust pre-commit configuration

## 0.1.3

> 📅 2026-01-23

- 🐛 Fixed: Python 3.11 compatibility (added `typing_extensions` dependency)

## 0.1.2

> 📅 2026-01-09

- ⛓️‍💥 Breaking:
    - http/stdio transport is now a required command line argument, user should choose either `http` or `stdio`, `stdio` is the default.

- 🆕 New:
    - Added Authorization bearer token verification
    - Added `--log-level` command line argument

- 🗑️ Removed:
    - Removed the feature that http/stdio transports run at the same

## 0.1.1

> 📅 2026-01-06

An early release.
