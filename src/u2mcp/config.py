"""Config file discovery and cyclopts loader construction."""

from __future__ import annotations

import logging
import stat
import sys
from collections import OrderedDict
from collections.abc import Mapping, Sequence
from pathlib import Path

from cyclopts.config import ConfigFromFile, Json, Toml, Yaml
from platformdirs import site_config_dir, user_config_dir
from rich.console import Console
from rich.panel import Panel

if __package__ is None:
    raise RuntimeError("Must be run as a module")

APP_NAME = __package__

EXTENSION_MAP: Mapping[str, type[ConfigFromFile]] = OrderedDict(
    {
        ".toml": Toml,
        ".yaml": Yaml,
        ".yml": Yaml,
        ".json": Json,
    }
)

CONFIG_FILENAMES = tuple(f"{APP_NAME}{ext}" for ext in EXTENSION_MAP.keys())

ENV_PREFIX = f"{APP_NAME.upper()}_"


def get_system_config_dir() -> Path:
    """Return platform-specific system config directory."""
    return Path(site_config_dir(APP_NAME, appauthor=False))


def get_user_config_dir() -> Path:
    """Return platform-specific user config directory."""
    return Path(user_config_dir(APP_NAME, appauthor=False))


def first_config_in_dir(directory: Path, filenames: Sequence[str]) -> Path | None:
    """Return the first existing config file in a directory, or None."""
    for file in filenames:
        if (pth := directory / file).is_file():
            return pth
    return None


def discover_config_files() -> Sequence[Path]:
    """Discover config files from system, user, and cwd directories.

    Returns files in priority order (system < user < cwd).
    At most one file per directory (first match wins).
    """
    files: list[Path] = []
    for directory in (get_system_config_dir(), get_user_config_dir(), Path.cwd()):
        if not directory.is_dir():
            continue
        if (found := first_config_in_dir(directory, CONFIG_FILENAMES)) is not None:
            files.append(found)
    return files


def build_config_loaders(files: Sequence[Path]) -> Sequence[ConfigFromFile]:
    """Create cyclopts config loaders for the given files."""
    loaders: list[ConfigFromFile] = []
    for path in files:
        loader_cls = EXTENSION_MAP.get(path.suffix.lower())
        if loader_cls is not None:
            loaders.append(loader_cls(path=path, must_exist=False))
    return loaders


def _exit_with_error(message: str, *, exit_code: int = 1) -> None:
    """Print a formatted error panel and exit."""
    Console(stderr=True).print(Panel(message, title="Error", border_style="red"))
    sys.exit(exit_code)


def resolve_config(config_file: Path | None = None) -> Sequence[ConfigFromFile]:
    """Resolve config loaders based on explicit file or auto-discovery.

    If config_file is provided, use only that file.
    Otherwise auto-discover from system/user/cwd directories.
    """
    loaders: list[ConfigFromFile] = []
    log = logging.getLogger(__name__)

    if config_file is not None:
        try:
            st = config_file.stat()
        except FileNotFoundError:
            _exit_with_error(f"Config file not found: {config_file}")
        except PermissionError:
            _exit_with_error(f"Permission denied: cannot access config file {config_file}")
        except OSError as e:
            _exit_with_error(f"Cannot access config file {config_file}: {e}")
        if not stat.S_ISREG(st.st_mode):
            _exit_with_error(f"Config path is not a file: {config_file}")
        loader_cls = EXTENSION_MAP.get(config_file.suffix.lower())
        if loader_cls is None:
            _exit_with_error(
                f"Unsupported config file extension '{config_file.suffix}'.\nSupported: {', '.join(sorted(EXTENSION_MAP))}"
            )
        else:
            log.debug("Using config file: %s", config_file)
            loaders.append(loader_cls(path=config_file, must_exist=True))
    else:
        loaders.extend(build_config_loaders(discover_config_files()))
        for loader in loaders:
            log.debug("Using config file: %s", getattr(loader, "path", None))

    return loaders
