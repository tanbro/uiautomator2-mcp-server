# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import copy_metadata

a = Analysis(
    ['main.py'],
    datas=copy_metadata('uiautomator2-mcp-server', recursive=True),
)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, exclude_binaries=True, name='u2mcp')
coll = COLLECT(exe, a.binaries, a.datas, name='u2mcp')
