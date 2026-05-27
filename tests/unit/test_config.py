"""Unit tests for config file discovery and loader construction."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from cyclopts.config import Json, Toml, Yaml

from u2mcp.config import (
    APP_NAME,
    build_config_loaders,
    discover_config_files,
    get_system_config_dir,
    get_user_config_dir,
    resolve_config,
)


@pytest.mark.unit
class TestConfigDirs:
    def test_system_config_dir_returns_path(self):
        result = get_system_config_dir()
        assert isinstance(result, Path)
        assert APP_NAME in str(result)

    def test_user_config_dir_returns_path(self):
        result = get_user_config_dir()
        assert isinstance(result, Path)
        assert APP_NAME in str(result)


@pytest.mark.unit
class TestDiscoverConfigFiles:
    def test_no_config_files_found(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.chdir(tmp_path)
        with (
            patch("u2mcp.config.get_system_config_dir", return_value=tmp_path / "sys"),
            patch("u2mcp.config.get_user_config_dir", return_value=tmp_path / "user"),
        ):
            assert discover_config_files() == []

    def test_finds_config_in_cwd(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / f"{APP_NAME}.toml").write_text("check-adb = false\n")
        with (
            patch("u2mcp.config.get_system_config_dir", return_value=tmp_path / "sys"),
            patch("u2mcp.config.get_user_config_dir", return_value=tmp_path / "user"),
        ):
            files = discover_config_files()
        assert len(files) == 1
        assert files[0].suffix == ".toml"

    def test_priority_order(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.chdir(tmp_path)
        sys_dir = tmp_path / "sys"
        user_dir = tmp_path / "user"
        sys_dir.mkdir()
        user_dir.mkdir()
        (sys_dir / f"{APP_NAME}.toml").write_text('log-level = "error"\n')
        (user_dir / f"{APP_NAME}.yaml").write_text("log-level: warning\n")
        (tmp_path / f"{APP_NAME}.json").write_text('{"log-level": "debug"}')
        with (
            patch("u2mcp.config.get_system_config_dir", return_value=sys_dir),
            patch("u2mcp.config.get_user_config_dir", return_value=user_dir),
        ):
            files = discover_config_files()
        assert len(files) == 3
        # system < user < cwd
        assert files[0].parent == sys_dir
        assert files[1].parent == user_dir
        assert files[2].parent == tmp_path


@pytest.mark.unit
class TestBuildConfigLoaders:
    def test_toml_loader(self, tmp_path: Path):
        f = tmp_path / "config.toml"
        f.write_text("")
        loaders = build_config_loaders([f])
        assert len(loaders) == 1
        assert isinstance(loaders[0], Toml)

    def test_yaml_loader(self, tmp_path: Path):
        f = tmp_path / "config.yaml"
        f.write_text("")
        loaders = build_config_loaders([f])
        assert len(loaders) == 1
        assert isinstance(loaders[0], Yaml)

    def test_yml_loader(self, tmp_path: Path):
        f = tmp_path / "config.yml"
        f.write_text("")
        loaders = build_config_loaders([f])
        assert len(loaders) == 1
        assert isinstance(loaders[0], Yaml)

    def test_json_loader(self, tmp_path: Path):
        f = tmp_path / "config.json"
        f.write_text("{}")
        loaders = build_config_loaders([f])
        assert len(loaders) == 1
        assert isinstance(loaders[0], Json)

    def test_multiple_files(self, tmp_path: Path):
        files = [tmp_path / "config.toml", tmp_path / "config.json"]
        for f in files:
            f.write_text("{}" if f.suffix == ".json" else "")
        loaders = build_config_loaders(files)
        assert len(loaders) == 2
        assert isinstance(loaders[0], Toml)
        assert isinstance(loaders[1], Json)


@pytest.mark.unit
class TestResolveConfig:
    def test_explicit_file(self, tmp_path: Path):
        f = tmp_path / "my.toml"
        f.write_text("")
        loaders = resolve_config(f)
        assert len(loaders) == 1
        assert isinstance(loaders[0], Toml)

    def test_explicit_file_missing(self, tmp_path: Path):
        f = tmp_path / "missing.toml"
        with pytest.raises(SystemExit, match="Config file not found"):
            resolve_config(f)

    def test_unsupported_extension(self, tmp_path: Path):
        f = tmp_path / "config.ini"
        f.write_text("")
        from cyclopts.exceptions import ValidationError

        with pytest.raises(ValidationError):
            resolve_config(f)

    def test_auto_discover(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / f"{APP_NAME}.toml").write_text("check-adb = false\n")
        monkeypatch.delenv(f"{APP_NAME.upper()}_CONFIG_FILE", raising=False)
        with (
            patch("u2mcp.config.get_system_config_dir", return_value=tmp_path / "sys"),
            patch("u2mcp.config.get_user_config_dir", return_value=tmp_path / "user"),
        ):
            loaders = resolve_config(None)
        assert len(loaders) == 1
        assert isinstance(loaders[0], Toml)
