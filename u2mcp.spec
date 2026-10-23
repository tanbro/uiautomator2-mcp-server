# -*- mode: python

from PyInstaller.utils.hooks import collect_data_files, collect_submodules, copy_metadata

a = Analysis(  # type: ignore  # noqa: F821
    ["main.py"],
    datas=copy_metadata("uiautomator2-mcp-server", recursive=True) + collect_data_files("u2mcp"),
    hiddenimports=collect_submodules("u2mcp.tools"),
    excludes=[
        "mypy",
        "mypyc",
        # GUI toolkits never used by this CLI
        "tkinter",
        "_tkinter",
        # Unused stdlib bulk
        "pydoc_data",
        "curses",
        "test",
        # Packaging machinery not needed at runtime
        "setuptools",
        "pkg_resources",
        "pip",
        "wheel",
    ],
    noarchive=False,
)
pyz = PYZ(a.pure)  # type: ignore  # noqa: F821

# Drop Pillow codec/plugin binaries this app never uses
# (screenshots only need PNG/JPEG; AVIF alone is ~8MB).
PIL_DROPS = ("_avif", "_imagingtk", "_imagingcms", "_imagingmath", "_imagingquant")
a.binaries = [b for b in a.binaries if not any(d in b[0] for d in PIL_DROPS)]

exe = EXE(pyz, a.scripts, exclude_binaries=True, name="u2mcp", icon="NONE")  # type: ignore # noqa: F821
coll = COLLECT(exe, a.binaries, a.datas, name="u2mcp")  # type: ignore # noqa: F821
