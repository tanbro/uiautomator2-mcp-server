# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files, collect_submodules, copy_metadata

a = Analysis(
    ["main.py"],
    datas=copy_metadata("uiautomator2-mcp-server", recursive=True) + collect_data_files("u2mcp"),
    hiddenimports=collect_submodules("u2mcp.tools"),
    excludes=["mypy", "mypyc"],
)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, exclude_binaries=True, name="u2mcp")
coll = COLLECT(exe, a.binaries, a.datas, name="u2mcp")
