# CHANGELOG

## 0.2.0(developing)

> 📅 2026-01-31

- ⛓️‍💥 Breaking:
    - CLI now requires explicit subcommand (`http`, `stdio`, `tools`, `info`, `tags`, or `version`). Running `u2mcp` without arguments shows help instead of starting server with default stdio transport. Migrate by appending `stdio` to your command: `u2mcp` → `u2mcp stdio`

- 🆕 New:
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
    - Refactor CLI with Typer subcommands
    - Move tag parsing and wildcard expansion logic to mcp module
    - Rename `_version.py` to `version.py`
    - Rename `monitor_task_group` to `background_task_group`
    - Update `shell_command` to return exit code and output
    - Enhance ADB connectivity check with detailed information and platform-specific guidance

- 🐛 Fixed:
    - Add `serial_optional=None` parameter to argparse.Namespace in the init tool
    - Improve scrcpy error handling for process exit during startup
    - Correct scrcpy tool name and add Windows executable support

- 📚 Docs:
    - Add CLAUDE.md with comprehensive project documentation
    - Add CLI utility commands documentation to README
    - Add tool tagging system documentation
    - Add installation guides for uv and pipx
    - Add Chinese translation to README
    - Add code of conduct and contribution guidelines
    - Add ADB troubleshooting guidance

- 🧪 Tests:
    - Enhance u2 device mock with comprehensive functionality

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
