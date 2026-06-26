"""Tests for table_detector geometry helpers."""
from __future__ import annotations

from pdf2md.table_detector import _bboxes_overlap


class TestBboxesOverlap:
    def test_overlapping_boxes(self) -> None:
        assert _bboxes_overlap((0, 0, 10, 10), (5, 5, 15, 15)) is True

    def test_contained_box(self) -> None:
        assert _bboxes_overlap((0, 0, 100, 100), (10, 10, 20, 20)) is True

    def test_disjoint_horizontally(self) -> None:
        assert _bboxes_overlap((0, 0, 10, 10), (20, 0, 30, 10)) is False

    def test_disjoint_vertically(self) -> None:
        assert _bboxes_overlap((0, 0, 10, 10), (0, 20, 10, 30)) is False

    def test_edge_touching_is_not_overlap(self) -> None:
        # Shared edge only (x1 == bx0) — strict inequality means no overlap
        assert _bboxes_overlap((0, 0, 10, 10), (10, 0, 20, 10)) is False
