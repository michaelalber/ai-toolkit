"""Tests for the relationship cache.

Unlike the Phase 1 per-file sidecars, Phase 3 writes one aggregate RELATIONSHIPS.md,
so the cache must persist each file's *verified* triples — a skipped (unchanged) file
still needs to contribute its edges to the rebuilt document. Keyed by code SHA + model,
so a code or model change invalidates the entry.
"""
from __future__ import annotations

from pathlib import Path

from code2md.enrich.relate_cache import RelateCache
from code2md.enrich.relationships import Triple
from code2md.enrich.scandoc import ParsedScanDoc


def _doc(code: str = "x = 1") -> ParsedScanDoc:
    return ParsedScanDoc(
        doc_path=Path("/scan/a.py.md"),
        rel_doc_path=Path("a.py.md"),
        source="proj",
        path="a.py",
        language="python",
        code=code,
    )


class TestRelateCache:
    def test_roundtrip_persists_triples(self, tmp_path: Path) -> None:
        cache = RelateCache.load(tmp_path)
        doc = _doc()
        triples = [
            Triple("A", "uses", "B", domain="architecture", description="x", derived_from="a.py.md")
        ]
        assert not cache.is_fresh(doc, "m")
        cache.update(doc, "m", triples)
        cache.save()

        reloaded = RelateCache.load(tmp_path)
        assert reloaded.is_fresh(doc, "m")
        assert reloaded.get_triples(doc) == triples

    def test_stale_on_model_change(self, tmp_path: Path) -> None:
        cache = RelateCache.load(tmp_path)
        cache.update(_doc(), "m1", [Triple("A", "uses", "B")])
        assert cache.is_fresh(_doc(), "m1")
        assert not cache.is_fresh(_doc(), "m2")

    def test_stale_on_code_change(self, tmp_path: Path) -> None:
        cache = RelateCache.load(tmp_path)
        cache.update(_doc("x = 1"), "m", [Triple("A", "uses", "B")])
        assert not cache.is_fresh(_doc("x = 2"), "m")

    def test_empty_triples_are_cached(self, tmp_path: Path) -> None:
        # A file with no edges is still "done" — don't re-extract it every run.
        cache = RelateCache.load(tmp_path)
        cache.update(_doc(), "m", [])
        cache.save()
        reloaded = RelateCache.load(tmp_path)
        assert reloaded.is_fresh(_doc(), "m")
        assert reloaded.get_triples(_doc()) == []
