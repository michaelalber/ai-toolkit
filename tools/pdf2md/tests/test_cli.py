"""CLI integration tests using typer's test runner."""
from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from pdf2md.cli import app

runner = CliRunner()


class TestCLI:
    def test_version_flag(self) -> None:
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output

    def test_help_flag(self) -> None:
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Convert a PDF" in result.output

    def test_nonexistent_input_exits_with_error(self) -> None:
        result = runner.invoke(app, ["/nonexistent/path/to/file.pdf"])
        assert result.exit_code != 0

    def test_invalid_image_format_exits_with_error(self, simple_pdf: Path) -> None:
        result = runner.invoke(app, [str(simple_pdf), "--image-format", "bmp"])
        assert result.exit_code == 1

    def test_single_pdf_produces_md_file(self, simple_pdf: Path, tmp_path: Path) -> None:
        output = tmp_path / "out.md"
        result = runner.invoke(app, [str(simple_pdf), str(output), "--no-images"])
        assert result.exit_code == 0, result.output
        assert output.exists()
        content = output.read_text()
        assert len(content) > 0

    def test_metadata_flag_adds_front_matter(self, simple_pdf: Path, tmp_path: Path) -> None:
        output = tmp_path / "out.md"
        runner.invoke(app, [str(simple_pdf), str(output), "--no-images", "--metadata"])
        content = output.read_text()
        assert content.startswith("---")
        assert "source:" in content

    def test_headings_pdf_contains_hash_headings(self, headings_pdf: Path, tmp_path: Path) -> None:
        output = tmp_path / "headings.md"
        runner.invoke(app, [str(headings_pdf), str(output), "--no-images"])
        content = output.read_text()
        assert "#" in content

    def test_page_range_limits_output(self, multipage_pdf: Path, tmp_path: Path) -> None:
        full_out = tmp_path / "full.md"
        partial_out = tmp_path / "partial.md"
        runner.invoke(app, [str(multipage_pdf), str(full_out), "--no-images"])
        runner.invoke(app, [str(multipage_pdf), str(partial_out), "--no-images", "--page-range", "1-2"])
        full_len = len(full_out.read_text())
        partial_len = len(partial_out.read_text())
        assert partial_len < full_len

    def test_batch_mode_converts_directory(self, tmp_path: Path, simple_pdf: Path, headings_pdf: Path) -> None:
        # Copy fixtures into a temp input dir
        import shutil

        input_dir = tmp_path / "pdfs"
        input_dir.mkdir()
        shutil.copy(simple_pdf, input_dir / "simple.pdf")
        shutil.copy(headings_pdf, input_dir / "headings.pdf")

        output_dir = tmp_path / "out"
        result = runner.invoke(app, [str(input_dir), str(output_dir), "--no-images"])
        assert result.exit_code == 0
        assert (output_dir / "simple.md").exists()
        assert (output_dir / "headings.md").exists()
