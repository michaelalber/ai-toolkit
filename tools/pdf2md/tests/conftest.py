"""Shared pytest fixtures that generate minimal PDF files at test time.

PDFs are created via reportlab so no binary test assets need to be committed.
All fixtures are session-scoped to avoid regenerating on every test.
"""
from __future__ import annotations

from pathlib import Path

import pytest


def _make_canvas(path: Path):
    from reportlab.pdfgen import canvas  # type: ignore[import-untyped]

    return canvas.Canvas(str(path))


@pytest.fixture(scope="session")
def simple_pdf(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Single-page PDF with plain body text only."""
    from reportlab.lib.units import inch  # type: ignore[import-untyped]

    p = tmp_path_factory.mktemp("fixtures") / "simple.pdf"
    c = _make_canvas(p)
    c.setFont("Helvetica", 12)
    c.drawString(inch, 10 * inch, "This is a simple paragraph of body text.")
    c.drawString(inch, 9.5 * inch, "It spans two lines in the fixture PDF.")
    c.save()
    return p


@pytest.fixture(scope="session")
def headings_pdf(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Single-page PDF with three heading sizes plus body text."""
    from reportlab.lib.units import inch  # type: ignore[import-untyped]

    p = tmp_path_factory.mktemp("fixtures") / "headings.pdf"
    c = _make_canvas(p)
    # H1 equivalent (~24pt)
    c.setFont("Helvetica-Bold", 24)
    c.drawString(inch, 10 * inch, "Document Title")
    # H2 equivalent (~18pt)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(inch, 9 * inch, "Section Heading")
    # H3 equivalent (~14pt bold)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(inch, 8 * inch, "Subsection")
    # Body
    c.setFont("Helvetica", 11)
    c.drawString(inch, 7 * inch, "Body paragraph text here.")
    c.save()
    return p


@pytest.fixture(scope="session")
def code_pdf(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Single-page PDF with a monospace code block."""
    from reportlab.lib.units import inch  # type: ignore[import-untyped]

    p = tmp_path_factory.mktemp("fixtures") / "code.pdf"
    c = _make_canvas(p)
    c.setFont("Helvetica", 12)
    c.drawString(inch, 10 * inch, "Example function:")
    c.setFont("Courier", 10)
    c.drawString(inch, 9.5 * inch, "def hello():")
    c.drawString(inch, 9.2 * inch, '    print("Hello, world!")')
    c.save()
    return p


@pytest.fixture(scope="session")
def multipage_pdf(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Five-page PDF with a consistent running header on every page."""
    from reportlab.lib.units import inch  # type: ignore[import-untyped]

    p = tmp_path_factory.mktemp("fixtures") / "multipage.pdf"
    c = _make_canvas(p)
    for page_num in range(1, 6):
        c.setFont("Helvetica", 8)
        c.drawString(inch, 10.8 * inch, "Running Header")
        c.setFont("Helvetica-Bold", 20)
        c.drawString(inch, 10 * inch, f"Chapter {page_num}")
        c.setFont("Helvetica", 12)
        c.drawString(inch, 9 * inch, f"Content of page {page_num}.")
        c.setFont("Helvetica", 8)
        c.drawString(inch, 0.5 * inch, str(page_num))
        if page_num < 5:
            c.showPage()
    c.save()
    return p
