# nuitka-project: --mode=standalone
# nuitka-project: --output-filename=u2mcp
# nuitka-project: --nofollow-import-to=mypy

if __name__ == "__main__":
    from u2mcp.__main__ import main

    main()
