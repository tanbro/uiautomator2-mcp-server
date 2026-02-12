# Publishing the u2mcp Alias Package

This document describes how to publish the `u2mcp` alias package to PyPI.

## What is the u2mcp Alias Package?

The `u2mcp` package is a thin alias that:
1. Depends on `uiautomator2-mcp-server>=0.3.0`
2. Provides the `u2mcp` CLI entry point
3. Allows users to `pip install u2mcp` or `uvx u2mcp stdio`

## Why Publish an Alias?

- ✅ Reserves the `u2mcp` name on PyPI
- ✅ Enables `uvx u2mcp stdio` for convenient usage
- ✅ Smooth transition path to v1.0.0 when we flip the names

## Building and Publishing

### Step 1: Prepare Build Directory

```bash
# Create a temporary build directory
mkdir /tmp/u2mcp-build
cd /tmp/u2mcp-build
```

### Step 2: Copy Files

```bash
# Copy the alias configuration
cp /path/to/uiautomator2-mcp-server/pyproject-u2mcp-alias.toml pyproject.toml

# Copy the README
cp /path/to/uiautomator2-mcp-server/README-ALIAS.md README.md

# Create the u2mcp package directory
mkdir u2mcp

# Copy the init file
cp /path/to/uiautomator2-mcp-server/u2mcp-alias-init.py u2mcp/__init__.py
```

### Step 3: Build

```bash
# Build the package
uv build --out-dir dist/
```

This will create:
- `dist/u2mcp-0.3.0-py3-none-any.whl`
- `dist/u2mcp-0.3.0.tar.gz`

### Step 4: Check Package Contents

```bash
# Inspect the wheel to ensure it's correct
unzip -l dist/u2mcp-0.3.0-py3-none-any.whl
```

Expected contents:
- `u2mcp/__init__.py` - Our init file
- `u2mcp-0.3.0.dist-info/` - Metadata
- `u2mcp-0.3.0.dist-info/entry_points.txt` - Should contain `u2mcp = u2mcp.__main__:main`

### Step 5: Publish to PyPI

```bash
# Publish (requires PyPI token)
uv publish dist/u2mcp-0.3.0-*.whl dist/u2mcp-0.3.0-*.tar.gz
```

## Verification

After publishing, verify:

```bash
# Test installing from PyPI
pip install u2mcp

# Verify the CLI works
u2mcp --version

# Test uvx (in a clean environment)
uvx u2mcp --version
```

## Version Strategy

The `u2mcp` alias package version should track with `uiautomator2-mcp-server`:

| uiautomator2-mcp-server | u2mcp alias |
|-------------------------|-------------|
| 0.3.0                   | 0.3.0       |
| 0.4.0                   | 0.4.0       |
| 1.0.0                   | 1.0.0       |

## Migration Plan (v1.0.0)

In v1.0.0:
- `u2mcp` becomes the primary package
- `uiautomator2-mcp-server` becomes a legacy alias
- Both packages install the same code

## Files Reference

- `pyproject-u2mcp-alias.toml` - Package configuration
- `README-ALIAS.md` - Package README
- `u2mcp-alias-init.py` - Package init file
