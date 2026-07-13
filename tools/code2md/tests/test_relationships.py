"""Tests for Phase 3 relationship extraction data model + validation.

The controlled vocabularies (VALID_RELATIONS / VALID_DOMAINS / VALID_TYPES) are
*vendored* from grounded-code-mcp's ``graph/graph_store.py`` — the two live in
separate repos so we can't import. These tests pin the contract: an extracted
edge's verb, once normalised the same way grounded's ``graph_builder`` does, must
land in VALID_RELATIONS or the parser would silently drop it.
"""
from __future__ import annotations

import pytest

from code2md.enrich.relationships import (
    VALID_DOMAINS,
    VALID_RELATIONS,
    VALID_TYPES,
    Triple,
    normalize_relation,
    parse_extraction_json,
)


class TestVocab:
    def test_relations_include_known_code_verbs(self) -> None:
        # A representative sample from grounded graph_store.VALID_RELATIONS.
        for verb in ("orchestrates", "uses", "calls", "produces", "wraps", "contains"):
            assert verb in VALID_RELATIONS
        # Guard against accidental truncation of the vendored set.
        assert len(VALID_RELATIONS) >= 90

    def test_domains_and_types(self) -> None:
        assert {"architecture", "python"} <= VALID_DOMAINS
        assert len(VALID_DOMAINS) == 15
        assert VALID_TYPES == frozenset({"pattern", "principle", "practice", "anti-pattern"})


class TestNormalizeRelation:
    @pytest.mark.parametrize(
        ("raw", "expected"),
        [
            ("orchestrates", "orchestrates"),
            ("USES", "uses"),
            ("composes with", "composes-with"),  # spaces -> hyphens
            ("composed_by", "composed-by"),  # underscores -> hyphens
            ("  calls  ", "calls"),  # trimmed
        ],
    )
    def test_valid_verbs_normalize(self, raw: str, expected: str) -> None:
        assert normalize_relation(raw) == expected

    @pytest.mark.parametrize("raw", ["frobnicates", "does-a-thing", ""])
    def test_invalid_verbs_return_none(self, raw: str) -> None:
        assert normalize_relation(raw) is None


class TestParseExtractionJson:
    def test_valid_edges_become_triples(self) -> None:
        text = """
        {"relationships": [
          {"subject": "IngestionPipeline", "relation": "orchestrates",
           "object": "DocumentParser", "domain": "architecture", "type": "",
           "description": "parse step"},
          {"subject": "DocumentChunker", "relation": "produces",
           "object": "Chunk", "domain": "python"}
        ]}
        """
        triples = parse_extraction_json(text, derived_from="src/ingest.py.md")
        assert len(triples) == 2
        first = triples[0]
        assert first == Triple(
            subject="IngestionPipeline",
            relation="orchestrates",
            obj="DocumentParser",
            domain="architecture",
            node_type="",
            description="parse step",
            derived_from="src/ingest.py.md",
        )
        assert triples[1].domain == "python"

    def test_drops_invalid_relation(self) -> None:
        text = (
            '{"relationships": ['
            '{"subject": "A", "relation": "frobnicates", "object": "B"},'
            '{"subject": "A", "relation": "calls", "object": "B"}]}'
        )
        triples = parse_extraction_json(text)
        assert [t.relation for t in triples] == ["calls"]

    def test_normalizes_verb_and_stores_it(self) -> None:
        text = '{"relationships": [{"subject": "A", "relation": "Composes With", "object": "B"}]}'
        assert parse_extraction_json(text)[0].relation == "composes-with"

    def test_drops_edges_missing_subject_or_object(self) -> None:
        text = (
            '{"relationships": ['
            '{"subject": "", "relation": "calls", "object": "B"},'
            '{"subject": "A", "relation": "calls", "object": ""},'
            '{"relation": "calls", "object": "B"}]}'
        )
        assert parse_extraction_json(text) == []

    def test_invalid_domain_falls_back_to_architecture(self) -> None:
        text = (
            '{"relationships": [{"subject": "A", "relation": "uses", '
            '"object": "B", "domain": "banana"}]}'
        )
        assert parse_extraction_json(text)[0].domain == "architecture"

    def test_invalid_type_becomes_blank(self) -> None:
        text = (
            '{"relationships": [{"subject": "A", "relation": "uses", '
            '"object": "B", "type": "widget"}]}'
        )
        assert parse_extraction_json(text)[0].node_type == ""

    def test_malformed_json_returns_empty(self) -> None:
        assert parse_extraction_json("not json at all") == []
        assert parse_extraction_json('{"relationships": "nope"}') == []
        assert parse_extraction_json("[]") == []
