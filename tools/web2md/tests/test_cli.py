"""CLI integration tests — docling and httpx calls are mocked."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from web2md.cli import app

runner = CliRunner()


def _mock_dc_returning(text: str) -> MagicMock:
    mock = MagicMock()
    mock.return_value.convert.return_value.document.export_to_markdown.return_value = text
    return mock


class TestCLIFlags:
    def test_version_flag(self) -> None:
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output

    def test_help_flag(self) -> None:
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Markdown" in result.output

    def test_crawl_and_sitemap_mutually_exclusive(self) -> None:
        result = runner.invoke(app, ["https://example.com/", "--crawl", "--sitemap"])
        assert result.exit_code == 1


class TestSinglePage:
    @patch("web2md.converter.DocumentConverter", _mock_dc_returning("# Hello\n\nWorld.\n"))
    def test_produces_md_file(self, tmp_path: Path) -> None:
        out = tmp_path / "out.md"
        result = runner.invoke(app, ["https://example.com/", str(out)])
        assert result.exit_code == 0, result.output
        assert out.exists()
        assert "Hello" in out.read_text()

    @patch("web2md.converter.DocumentConverter", _mock_dc_returning("# Page\n"))
    def test_metadata_flag_adds_front_matter(self, tmp_path: Path) -> None:
        out = tmp_path / "out.md"
        runner.invoke(app, ["https://example.com/", str(out), "--metadata"])
        content = out.read_text()
        assert content.startswith("---")
        assert "source:" in content

    @patch("web2md.converter.DocumentConverter", _mock_dc_returning("# A\n\nBody A.\n\n# B\n\nBody B.\n"))
    def test_chunk_by_heading_creates_multiple_files(self, tmp_path: Path) -> None:
        out = tmp_path / "page.md"
        result = runner.invoke(app, ["https://example.com/", str(out), "--chunk-by-heading"])
        assert result.exit_code == 0, result.output
        md_files = list(tmp_path.glob("*.md"))
        assert len(md_files) == 2

    @patch("web2md.converter.DocumentConverter", _mock_dc_returning("![img](img.png)\n\nBody.\n"))
    def test_no_images_strips_images(self, tmp_path: Path) -> None:
        out = tmp_path / "out.md"
        runner.invoke(app, ["https://example.com/", str(out), "--no-images"])
        assert "![" not in out.read_text()

    @patch("web2md.converter.DocumentConverter", _mock_dc_returning("| A | B |\n| - | - |\n| 1 | 2 |\n"))
    def test_no_tables_strips_tables(self, tmp_path: Path) -> None:
        out = tmp_path / "out.md"
        runner.invoke(app, ["https://example.com/", str(out), "--no-tables"])
        assert "|" not in out.read_text()


class TestBatchSitemap:
    @patch("web2md.sitemap.fetch_sitemap_urls")
    @patch("web2md.converter.DocumentConverter", _mock_dc_returning("# Page\n"))
    def test_sitemap_mode_writes_one_file_per_url(
        self, mock_sitemap: MagicMock, tmp_path: Path
    ) -> None:
        mock_sitemap.return_value = [
            "https://example.com/",
            "https://example.com/about",
        ]
        out_dir = tmp_path / "out"
        result = runner.invoke(app, ["https://example.com/sitemap.xml", str(out_dir), "--sitemap"])
        assert result.exit_code == 0, result.output
        md_files = list(out_dir.glob("*.md"))
        assert len(md_files) == 2

    @patch("web2md.sitemap.fetch_sitemap_urls")
    @patch("web2md.converter.DocumentConverter", _mock_dc_returning("# Page\n"))
    def test_sitemap_max_pages_respected(
        self, mock_sitemap: MagicMock, tmp_path: Path
    ) -> None:
        mock_sitemap.return_value = [f"https://example.com/p{i}" for i in range(10)]
        out_dir = tmp_path / "out"
        runner.invoke(
            app, ["https://example.com/sitemap.xml", str(out_dir), "--sitemap", "--max-pages", "3"]
        )
        md_files = list(out_dir.glob("*.md"))
        assert len(md_files) <= 3


class TestBatchCrawl:
    @patch("web2md.crawler.crawl")
    @patch("web2md.converter.DocumentConverter", _mock_dc_returning("# Crawled\n"))
    def test_crawl_mode_writes_output_dir(
        self, mock_crawl: MagicMock, tmp_path: Path
    ) -> None:
        mock_crawl.return_value = ["https://example.com/", "https://example.com/about"]
        out_dir = tmp_path / "out"
        result = runner.invoke(app, ["https://example.com/", str(out_dir), "--crawl"])
        assert result.exit_code == 0, result.output
        md_files = list(out_dir.glob("*.md"))
        assert len(md_files) == 2
