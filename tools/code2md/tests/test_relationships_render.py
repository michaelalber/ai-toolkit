"""Tests for rendering triples into a parser-valid RELATIONSHIPS.md.

The acceptance bar is *parseability by grounded-code-mcp*. Since the two repos are
separate, this test vendors grounded's actual triple + section regexes
(``graph/graph_builder.py``) and asserts the rendered document round-trips through
them — every emitted triple parses, with the expected verb, concepts, and brackets.
"""
from __future__ import annotations

import re

from code2md.enrich.relationships import Triple, render_relationships

# --- Vendored from grounded-code-mcp graph/graph_builder.py -------------------
_ARROW = r"(?:→|->)"
_TRIPLE_RE = re.compile(
    rf'"([^"]+)"\s*{_ARROW}\s*([\w][\w-]*(?:\s+[\w][\w-]*)*)\s*{_ARROW}\s*"([^"]+)"'
    r"(?:\s*\[([^\]]*)\])?"  # source_slug
    r"(?:\s*\[([^\]]*)\])?"  # domain
    r"(?:\s*\[([^\]]*)\])?"  # type
    r"(?:\s*\[([^\]]*)\])?"  # description
)
_SECTION_DOMAIN_RE = re.compile(r"##[^<]+<!--\s*domain:\s*([\w-]+)\s*-->")


def _sample_triples() -> list[Triple]:
    return [
        Triple("IngestionPipeline", "orchestrates", "DocumentParser",
               domain="architecture", description="parse step",
               derived_from="src/ingest.py.md"),
        Triple("IngestionPipeline", "uses", "EmbeddingClient",
               domain="architecture", derived_from="src/ingest.py.md"),
        Triple("DocumentChunker", "produces", "Chunk",
               domain="python", derived_from="src/chunking.py.md"),
    ]


class TestRenderRelationships:
    def test_every_triple_parses_with_grounded_regex(self) -> None:
        out = render_relationships(_sample_triples(), "grounded-code-mcp", "big-model-cloud")
        parsed = [
            m.groups()
            for line in out.splitlines()
            if (m := _TRIPLE_RE.search(line.strip()))
        ]
        assert len(parsed) == 3
        subj, rel, obj, slug, domain, ntype, desc = parsed[0]
        assert (subj, rel, obj) == ("IngestionPipeline", "orchestrates", "DocumentParser")
        assert slug == "grounded-code-mcp"  # per-edge source attribution
        assert domain == "architecture"
        assert ntype == ""  # concrete code entity -> blank type bracket
        assert desc == "parse step"

    def test_bracket_order_is_slug_domain_type_desc(self) -> None:
        out = render_relationships(_sample_triples(), "grounded-code-mcp", "m")
        # The chunking edge carries the python domain and no description.
        line = next(ln for ln in out.splitlines() if "DocumentChunker" in ln)
        m = _TRIPLE_RE.search(line.strip())
        assert m is not None
        _, _, _, slug, domain, ntype, desc = m.groups()
        assert (slug, domain, ntype, desc) == ("grounded-code-mcp", "python", "", "")

    def test_section_header_sets_matching_domain(self) -> None:
        out = render_relationships(_sample_triples(), "grounded-code-mcp", "m")
        domains = _SECTION_DOMAIN_RE.findall(out)
        # One section per distinct domain present, and each is a valid grounded domain.
        assert set(domains) == {"architecture", "python"}

    def test_provenance_front_matter(self) -> None:
        out = render_relationships(_sample_triples(), "grounded-code-mcp", "big-model-cloud",
                                   generated_at="2026-07-05T00:00:00Z")
        assert out.startswith("---\n")
        assert "generated: true" in out
        assert "model: big-model-cloud" in out
        assert "generated_at: 2026-07-05T00:00:00Z" in out
        assert "kind: concept-relationships" in out
        assert "source: grounded-code-mcp" in out

    def test_quotes_and_brackets_in_names_are_sanitized(self) -> None:
        # A stray " in a concept or ] in a description must not break parsing.
        triples = [
            Triple('Weird"Name', "uses", "B]roken",
                   domain="architecture", description="see [here] now"),
        ]
        out = render_relationships(triples, "proj", "m")
        matches = [m for line in out.splitlines() if (m := _TRIPLE_RE.search(line.strip()))]
        assert len(matches) == 1  # still exactly one parseable triple

    def test_empty_triples_still_valid_document(self) -> None:
        out = render_relationships([], "grounded-code-mcp", "m")
        assert out.startswith("---\n")
        assert not _TRIPLE_RE.search(out)
