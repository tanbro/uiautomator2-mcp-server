from sys import exit

from .mcp import mcp
from .tools import *


def main():
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    exit(main())
