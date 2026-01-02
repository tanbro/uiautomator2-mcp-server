import logging

logging.getLogger("mcp.server").setLevel(logging.WARNING)
logging.getLogger("sse_starlette").setLevel(logging.WARNING)
logging.getLogger("docket").setLevel(logging.WARNING)
logging.getLogger("fakeredis").setLevel(logging.WARNING)

logging.basicConfig(level=logging.DEBUG)

# 确保有处理器
if not logging.root.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(levelname)s %(name)s - %(message)s")
    handler.setFormatter(formatter)
    logging.root.addHandler(handler)
