from __future__ import annotations

from typing import Literal

# ToolTagsT = Literal[]
HealthCheckCategorieT = Literal["environment", "adb", "devices", "u2_init", "mcp_tools", "scrcpy"]

# XPathElement.swipe delegates to swipe_in_bounds (uiautomator2/utils.py),
# which raises ValueError for anything outside these four.
SwipeDirectionType = Literal["left", "right", "up", "down"]

# XPathElement.scroll remaps only these two onto Direction.FORWARD/BACKWARD.
XpathScrollDirectionType = Literal["forward", "backward"]

# Image formats for capture tools (also valid as PIL save format and data URL subtype).
ImageFormatType = Literal["jpeg", "png"]
