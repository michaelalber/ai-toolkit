"""Unit tests for converter.py — docling calls are mocked."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from web2md.converter import build_front_matter, convert_and_write, write_chunks
from web2md.models import ConversionConfig


def _make_config(url: str, output: Path, **kwargs: object) -> ConversionConfig:
    return ConversionConfig(url=url, output_path=output, **kwargs)  # type: ignore[arg-type]


class TestBuildFrontMatter:
    def test_contains_source_url(self) -> None:
        fm = build_front_matter("https://example.com/page")
        assert "source: https://example.com/page" in fm

    def test_contains_tool_field(self) -> None:
        fm = build_front_matter("https://example.com/")
        assert "tool: web2md/" in fm

    def test_starts_and_ends_with_dashes(self) -> None:
        fm = build_front_matter("https://example.com/")
        assert fm.startswith("---\n")
        assert "---\n\n" in fm


class TestWriteChunks:
    def test_splits_at_h1(self, tmp_path: Path) -> None:
        markdown = "# First\n\nBody one.\n\n# Second\n\nBody two.\n"
        base = tmp_path / "page.md"
        written = write_chunks(markdown, base)
        assert len(written) == 2

    def test_preamble_file_when_no_leading_h1(self, tmp_path: Path) -> None:
        markdown = "Some intro.\n\n# Section\n\nContent.\n"
        base = tmp_path / "page.md"
        written = write_chunks(markdown, base)
        names = [p.name for p in written]
        assert any("preamble" in n for n in names)

    def test_single_chunk_when_no_h1(self, tmp_path: Path) -> None:
        markdown = "Just a paragraph.\n"
        base = tmp_path / "page.md"
        written = write_chunks(markdown, base)
        assert len(written) == 1


class TestConvertAndWrite:
    def _mock_docling(self, markdown_text: str) -> MagicMock:
        mock_result = MagicMock()
        mock_result.document.export_to_markdown.return_value = markdown_text
        mock_converter = MagicMock()
        mock_converter.return_value.convert.return_value = mock_result
        return mock_converter

    @patch("web2md.converter.DocumentConverter")
    def test_writes_file(self, mock_dc: MagicMock, tmp_path: Path) -> None:
        mock_dc.return_value.convert.return_value.document.export_to_markdown.return_value = (
            "# Hello\n"
        )
        out = tmp_path / "out.md"
        cfg = _make_config("https://example.com/", out)
        convert_and_write(cfg)
        assert out.exists()
        assert "Hello" in out.read_text()

    @patch("web2md.converter.DocumentConverter")
    def test_metadata_prepends_front_matter(self, mock_dc: MagicMock, tmp_path: Path) -> None:
        mock_dc.return_value.convert.return_value.document.export_to_markdown.return_value = (
            "# Page\n"
        )
        out = tmp_path / "out.md"
        cfg = _make_config("https://example.com/", out, metadata=True)
        convert_and_write(cfg)
        content = out.read_text()
        assert content.startswith("---")
        assert "source:" in content

    @patch("web2md.converter.DocumentConverter")
    def test_no_images_strips_images(self, mock_dc: MagicMock, tmp_path: Path) -> None:
        mock_dc.return_value.convert.return_value.document.export_to_markdown.return_value = (
            "# Page\n\n![alt](img.png)\n\nBody.\n"
        )
        out = tmp_path / "out.md"
        cfg = _make_config("https://example.com/", out, no_images=True)
        convert_and_write(cfg)
        assert "![" not in out.read_text()

    @patch("web2md.converter.DocumentConverter")
    def test_no_tables_strips_tables(self, mock_dc: MagicMock, tmp_path: Path) -> None:
        mock_dc.return_value.convert.return_value.document.export_to_markdown.return_value = (
            "# Page\n\n| A | B |\n| - | - |\n| 1 | 2 |\n"
        )
        out = tmp_path / "out.md"
        cfg = _make_config("https://example.com/", out, no_tables=True)
        convert_and_write(cfg)
        assert "|" not in out.read_text()

    @patch("web2md.converter.DocumentConverter")
    def test_chunk_by_heading_creates_multiple_files(
        self, mock_dc: MagicMock, tmp_path: Path
    ) -> None:
        mock_dc.return_value.convert.return_value.document.export_to_markdown.return_value = (
            "# Alpha\n\nContent A.\n\n# Beta\n\nContent B.\n"
        )
        out = tmp_path / "page.md"
        cfg = _make_config("https://example.com/", out, chunk_by_heading=True)
        convert_and_write(cfg)
        md_files = list(tmp_path.glob("*.md"))
        assert len(md_files) == 2
