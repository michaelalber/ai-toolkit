"""Tests for engine selection and auto-detection."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from pdf2md.engines import DoclingEngine, FastEngine, select_engine
from pdf2md.engines.base import Engine


class TestEngineProtocol:
    def test_fast_engine_satisfies_protocol(self) -> None:
        assert isinstance(FastEngine(), Engine)

    def test_docling_engine_satisfies_protocol(self) -> None:
        assert isinstance(DoclingEngine(), Engine)


class TestSelectEngine:
    def test_fast_choice_returns_fast_engine(self, simple_pdf: Path) -> None:
        engine = select_engine("fast", simple_pdf)
        assert isinstance(engine, FastEngine)

    def test_docling_choice_returns_docling_engine(self, simple_pdf: Path) -> None:
        engine = select_engine("docling", simple_pdf)
        assert isinstance(engine, DoclingEngine)

    def test_auto_with_text_rich_pdf_returns_fast(self, headings_pdf: Path) -> None:
        # headings_pdf has enough extractable text (>50 chars/page) → FastEngine
        engine = select_engine("auto", headings_pdf)
        assert isinstance(engine, FastEngine)

    def test_auto_with_low_char_count_returns_docling(self, tmp_path: Path) -> None:
        # Patch _avg_chars to return a value below the threshold
        from pdf2md.engines import _avg_chars
        with patch("pdf2md.engines._avg_chars", return_value=5.0):
            engine = select_engine("auto", tmp_path / "fake.pdf")
        assert isinstance(engine, DoclingEngine)

    def test_auto_with_high_char_count_returns_fast(self, tmp_path: Path) -> None:
        with patch("pdf2md.engines._avg_chars", return_value=500.0):
            engine = select_engine("auto", tmp_path / "fake.pdf")
        assert isinstance(engine, FastEngine)


class TestAvgChars:
    def test_returns_float_for_valid_pdf(self, simple_pdf: Path) -> None:
        from pdf2md.engines import _avg_chars

        result = _avg_chars(simple_pdf)
        assert isinstance(result, float)
        assert result >= 0.0

    def test_returns_zero_for_nonexistent_file(self, tmp_path: Path) -> None:
        from pdf2md.engines import _avg_chars

        result = _avg_chars(tmp_path / "nonexistent.pdf")
        assert result == 0.0


class TestDoclingEngineImportError:
    def test_raises_runtime_error_when_docling_not_installed(
        self, simple_pdf: Path, tmp_path: Path
    ) -> None:
        import builtins

        from pdf2md.models import ConversionConfig

        real_import = builtins.__import__

        def mock_import(name: str, *args, **kwargs):
            if name == "docling.document_converter":
                raise ImportError("mocked missing docling")
            return real_import(name, *args, **kwargs)

        config = ConversionConfig(
            input_path=simple_pdf,
            output_path=tmp_path / "out.md",
            engine="docling",
        )
        engine = DoclingEngine()
        with patch("builtins.__import__", side_effect=mock_import):
            with pytest.raises(RuntimeError, match="Docling is not installed"):
                engine.convert(config)


class TestFastEngineConvert:
    def test_converts_simple_pdf_to_markdown(self, simple_pdf: Path, tmp_path: Path) -> None:
        from pdf2md.models import ConversionConfig

        config = ConversionConfig(
            input_path=simple_pdf,
            output_path=tmp_path / "out.md",
            no_images=True,
            engine="fast",
        )
        engine = FastEngine()
        result = engine.convert(config)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_does_not_prepend_metadata(self, simple_pdf: Path, tmp_path: Path) -> None:
        from pdf2md.models import ConversionConfig

        config = ConversionConfig(
            input_path=simple_pdf,
            output_path=tmp_path / "out.md",
            no_images=True,
            metadata=True,  # metadata is handled by converter, not the engine
            engine="fast",
        )
        engine = FastEngine()
        result = engine.convert(config)
        # Engine itself must NOT include front matter
        assert not result.startswith("---")
