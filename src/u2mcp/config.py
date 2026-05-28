"""Config file discovery and cyclopts loader construction."""

from __future__ import annotations

import logging
import sys
from collections import OrderedDict
from collections.abc import Mapping, Sequence
from pathlib import Path

from cyclopts.config import ConfigFromFile, Json, Toml, Yaml
from cyclopts.exceptions import ValidationError
from platformdirs import site_config_dir, user_config_dir

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


def resolve_config(config_file: Path | None = None) -> Sequence[ConfigFromFile]:
    """Resolve config loaders based on explicit file or auto-discovery.

    If config_file is provided, use only that file.
    Otherwise auto-discover from system/user/cwd directories.
    """
    loaders: list[ConfigFromFile] = []
    log = logging.getLogger(__name__)

    if config_file is not None:
        if not config_file.is_file():
            sys.exit(f"Error: Config file not found: {config_file}")
        loader_cls = EXTENSION_MAP.get(config_file.suffix.lower())
        if loader_cls is None:
            raise ValidationError(
                f"Unsupported config file extension '{config_file.suffix}'. Supported: {', '.join(sorted(EXTENSION_MAP))}"
            )
        log.debug("Using config file: %s", config_file)
        loaders.append(loader_cls(path=config_file, must_exist=False))
    else:
        loaders.extend(build_config_loaders(discover_config_files()))
        for loader in loaders:
            log.debug("Using config file: %s", getattr(loader, "path", None))

    return loaders
