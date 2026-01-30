# Contributing to uiautomator2-mcp-server

Thank you for your interest in contributing to uiautomator2-mcp-server! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

This project adheres to a code of conduct that all contributors are expected to follow:
- Be respectful and inclusive
- Provide constructive feedback
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Git
- ADB (Android Debug Bridge) - only needed for integration tests
- An Android device with USB debugging enabled - only needed for integration tests

### Setting Up Your Development Environment

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/your-username/uiautomator2-mcp-server.git
   cd uiautomator2-mcp-server
   ```

2. **Install development dependencies:**
   ```bash
   # Install uv (recommended)
   curl -LsSf https://astral.sh/uv/install.sh | sh  # Linux/macOS
   # or
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"  # Windows

   # Install dependencies using uv
   uv sync --dev
   ```

3. **Activate the virtual environment:**
   ```bash
   # Linux/macOS
   source .venv/bin/activate

   # Windows (PowerShell)
   .venv\Scripts\activate
   ```

4. **Install pre-commit hooks (highly recommended):**
   ```bash
   pre-commit install
   ```

   This will automatically run linters and formatters before each commit.

## Development Workflow

### Running Tests

We use pytest for testing. Tests are organized into:
- **Unit tests** (`tests/unit/`) - Fast tests that don't require external dependencies
- **Integration tests** (`tests/integration/`) - Tests that require a real Android device

```bash
# Run all tests
pytest

# Run only unit tests (fast, no device required)
pytest -m unit

# Run integration tests (requires Android device)
pytest -m integration

# Run with coverage report
pytest --cov=src/u2mcp --cov-report=html --cov-report=term-missing

# Run a specific test file
pytest tests/unit/test_device.py

# Run a specific test
pytest tests/unit/test_device.py::test_device_list
```

### Test Markers

We use pytest markers to categorize tests:
- `unit` - Unit tests (fast, no external dependencies)
- `integration` - Integration tests (require Android device)
- `slow` - Slow running tests
- `device` - Tests that require actual Android device

### Writing Tests

When adding new features, please include appropriate tests:

1. **Unit Tests:** Mock external dependencies (uiautomator2, adbutils)
   ```python
   from unittest.mock import AsyncMock, MagicMock, patch

   @pytest.mark.unit
   async def test_my_tool(mock_u2_device: MagicMock):
       # Arrange
       mock_u2_device.some_method.return_value = "expected"

       # Act
       result = await my_tool(serial="test-device")

       # Assert
       assert result == "expected"
   ```

2. **Integration Tests:** Test against real device (when applicable)
   ```python
   @pytest.mark.integration
   @pytest.mark.device
   async def test_my_tool_real_device():
       # This test requires a connected device
       result = await my_tool(serial="emulator-5554")
       assert result is not None
   ```

### Code Style

This project uses:
- **Ruff** for linting and formatting
- **mypy** for type checking
- **pre-commit** for automated checks

```bash
# Run linter
ruff check src/

# Auto-fix linting issues
ruff check --fix src/

# Format code
ruff format src/

# Type check
mypy src/
```

Pre-commit hooks will automatically run these checks before each commit if you have them installed.

### Project Structure

```
src/u2mcp/
├── __init__.py          # Package init, exports version info
├── __main__.py          # Entry point for CLI commands
├── _version.py          # Auto-generated version info (SCM)
├── mcp.py               # MCP server factory and configuration
├── background.py        # Background task management
├── health.py            # ADB availability check
└── tools/
    ├── __init__.py      # Tools registry
    ├── device.py        # Device management tools
    ├── action.py        # Touch/gesture tools
    ├── app.py           # App management tools
    ├── clipboard.py     # Clipboard read/write tools
    ├── element.py       # Element/UI interaction tools
    ├── misc.py          # Miscellaneous tools
    └── scrcpy.py        # Screen mirroring (scrcpy integration)

tests/
├── conftest.py          # Pytest configuration and fixtures
├── unit/                # Fast unit tests
└── integration/         # Integration tests requiring real devices
```

## Adding New Tools

To add a new MCP tool:

1. **Choose the appropriate module** in `src/u2mcp/tools/` based on functionality
2. **Create the tool function** with appropriate type hints:
   ```python
   from __future__ import annotations
   from typing import Any

   from u2mcp.mcp import mcp
   from u2mcp.device import get_device
   from anyio import to_thread

   @mcp.tool("my_tool")
   async def my_tool(serial: str, param: str) -> dict[str, Any]:
       """
       Brief description of what the tool does.

       Args:
           serial: Device serial number
           param: Description of parameter

       Returns:
           Dictionary with result information
       """
       async with get_device(serial) as device:
           result = await to_thread.run_sync(lambda: device.some_method(param))
       return {"result": result}
   ```

3. **Add tests** for the new tool in `tests/unit/` or `tests/integration/`
4. **Update documentation** in [README.md](README.md) if needed
5. **Run tests and linting** to ensure everything passes
6. **Commit and create a pull request**

## Pull Request Process

1. **Create a new branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

2. **Make your changes** following the guidelines above

3. **Commit your changes** with clear, descriptive messages:
   ```bash
   git add .
   git commit -m "feat: add new tool for XYZ"
   # Use conventional commits: feat:, fix:, docs:, chore:, etc.
   ```

4. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create a Pull Request** on GitHub with:
   - Clear title and description
   - Reference related issues (if any)
   - Screenshots or examples for UI changes (if applicable)
   - Confirmation that all tests pass
   - Confirmation that pre-commit hooks pass

### PR Review Checklist

Before submitting a PR, ensure:
- [ ] All tests pass (`pytest`)
- [ ] Code is formatted (`ruff format`)
- [ ] No linting errors (`ruff check`)
- [ ] Type checking passes (`mypy`)
- [ ] New features include tests
- [ ] Documentation is updated (if needed)
- [ ] Commit messages follow conventional commit format

## Release Process

Releases are managed by the maintainers through GitHub releases:

1. Maintainers create a new git tag following PEP 440 versioning
2. The CI pipeline automatically:
   - Validates the tag format
   - Runs all tests
   - Builds the package
   - Publishes to PyPI

Please don't create tags yourself unless you're a maintainer.

## Coverage Requirements

We aim to maintain good test coverage. Currently:
- CI runs coverage reports on all tests
- Coverage is uploaded to Codecov for tracking

**Goal:** We're working toward increasing coverage, especially in the `tools/` modules. Contributions that improve test coverage are highly appreciated!

## Getting Help

If you need help:
- Check existing [GitHub Issues](https://github.com/tanbro/uiautomator2-mcp-server/issues)
- Read the [README.md](README.md) for usage documentation
- Review existing tests for examples
- Ask questions in a new GitHub Issue with the `question` label

## License

By contributing to this project, you agree that your contributions will be licensed under the [GPL-3.0-or-later](LICENSE) license.

## Style Guidelines

### Python Code

- Use Python 3.11+ syntax
- All function signatures must include type hints
- Use `from __future__ import annotations` for deferred evaluation
- Use `typing_extensions` for compatibility with Python < 3.12
- Follow PEP 8 style guide (enforced by ruff)

### Documentation

- Use docstrings for all public functions, classes, and modules
- Keep docstrings clear and concise
- Update README.md when adding user-facing features

### Localization & Multi-language Policy

- Keep region-specific instructions (for example, Mainland China `pip`/`uv` mirror configuration) inside the corresponding language README (e.g., `README.zh-CN.md`).
- Do **not** duplicate region-only instructions into the English README. Instead, add a short navigation note in the English README pointing to the language specific file when appropriate (e.g., "See `README.zh-CN.md` for Mainland China-specific mirror instructions").
- Ensure translations are accurate and avoid adding region-specific content to all language files unless it is globally applicable.

### Async/Await

- Use `async/await` for all I/O operations
- Use `to_thread.run_sync()` for CPU-bound operations
- Use `get_device()` context manager for device access

Thank you for contributing to uiautomator2-mcp-server!
