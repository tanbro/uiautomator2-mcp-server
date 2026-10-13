"""
Unit tests for pure helpers in u2mcp.tools.device:
ensure_image, encode_image, save_image, filter_hierarchy_xml.
"""

from __future__ import annotations

import base64
import io
from pathlib import Path

import pytest
from lxml import etree
from PIL import Image as PILImage

from u2mcp.tools.device import (
    encode_image,
    ensure_image,
    filter_hierarchy_xml,
    save_image,
)


def _make_image(width: int = 4, height: int = 3, format: str = "PNG") -> PILImage.Image:
    im = PILImage.new("RGB", (width, height), color=(255, 0, 0))
    return im


@pytest.mark.unit
class TestEnsureImage:
    def test_returns_same_object_for_valid_image(self) -> None:
        im = _make_image()
        assert ensure_image(im) is im

    def test_raises_on_none(self) -> None:
        with pytest.raises(TypeError, match="Invalid image"):
            ensure_image(None)


@pytest.mark.unit
class TestEncodeImage:
    def test_returns_data_url_with_dimensions(self) -> None:
        im = _make_image(width=4, height=3)
        data_url, height, width = encode_image(im, "png")

        prefix = "data:image/png;base64,"
        assert data_url.startswith(prefix)
        # Round-trip the payload to prove it is a valid encoded image
        payload = base64.b64decode(data_url.removeprefix(prefix))
        decoded = PILImage.open(io.BytesIO(payload))
        assert decoded.size == (4, 3)
        assert (height, width) == (3, 4)

    def test_format_is_reflected_in_data_url(self) -> None:
        im = _make_image()
        data_url, _, _ = encode_image(im, "jpeg")
        assert data_url.startswith("data:image/jpeg;base64,")


@pytest.mark.unit
class TestSaveImage:
    def test_saves_to_nested_directory_and_returns_absolute_path(self, tmp_path: Path) -> None:
        target = tmp_path / "a" / "b" / "shot.png"
        im = _make_image()

        result = save_image(im, str(target))

        assert Path(result).is_absolute()
        assert Path(result) == target.resolve()
        assert target.is_file()
        with PILImage.open(target) as saved:
            assert saved.size == (4, 3)


@pytest.mark.unit
class TestFilterHierarchyXml:
    HIERARCHY = """
    <hierarchy>
        <node class="android.widget.Button" text="OK"/>
        <node class="android.widget.TextView" text="Hello"/>
    </hierarchy>
    """

    def test_returns_matching_nodes_joined_by_separator(self) -> None:
        result = filter_hierarchy_xml(self.HIERARCHY, '//node[@text="OK"]')
        assert "===" not in result
        assert 'text="OK"' in result

    def test_multiple_matches_are_separated(self) -> None:
        result = filter_hierarchy_xml(self.HIERARCHY, "//node")
        assert result.count("===") == 1
        assert 'text="OK"' in result and 'text="Hello"' in result

    def test_no_match_returns_empty_string(self) -> None:
        assert filter_hierarchy_xml(self.HIERARCHY, '//node[@text="missing"]') == ""

    def test_malformed_xml_raises(self) -> None:
        with pytest.raises(etree.XMLSyntaxError):
            filter_hierarchy_xml("<hierarchy><node>", "//node")
