import logging
from importlib import import_module
from sys import exit

# logging.basicConfig(level=logging.DEBUG)
# formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
# for hdl in logging.root.handlers:
#     hdl.setFormatter(formatter)

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(name)s - %(message)s",
    handlers=[logging.StreamHandler()],
    force=True,
)

logging.getLogger("mcp.server").setLevel(logging.WARNING)
logging.getLogger("sse_starlette").setLevel(logging.WARNING)
logging.getLogger("docket").setLevel(logging.WARNING)
logging.getLogger("fakeredis").setLevel(logging.WARNING)


def main():
    from .mcp import mcp

    import_module(".tools", "u2mcp")

    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    exit(main())
