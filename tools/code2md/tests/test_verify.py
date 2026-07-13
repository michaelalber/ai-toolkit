"""Tests for the edge verification pass — the guard against hallucinated routing.

Each extracted triple is re-checked against the exact code it was derived from; an
edge the code does not clearly support is dropped. Verification is conservative:
an unparseable or ambiguous verdict counts as unsupported.
"""
from __future__ import annotations

from code2md.enrich.relationships import Triple
from code2md.enrich.verify import (
    Verdict,
    build_verify_prompt,
    parse_verdict_json,
    verify_all,
    verify_triple,
)


class _FakeClient:
    """Returns a canned response per call; records the last prompt."""

    def __init__(self, *responses: str) -> None:
        self._responses = list(responses)
        self.last_prompt: str | None = None

    def generate(self, model: str, prompt: str, *, json_format: bool = True) -> str:
        self.last_prompt = prompt
        return self._responses.pop(0) if self._responses else '{"supported": false}'


def _triple(derived_from: str = "src/ingest.py.md") -> Triple:
    return Triple("IngestionPipeline", "uses", "EmbeddingClient",
                  domain="architecture", derived_from=derived_from)


class TestParseVerdict:
    def test_supported_true(self) -> None:
        assert parse_verdict_json('{"supported": true, "evidence": "line 12"}') == Verdict(
            True, "line 12"
        )

    def test_supported_false(self) -> None:
        assert parse_verdict_json('{"supported": false}').supported is False

    def test_unparseable_is_unsupported(self) -> None:
        # Conservative: uncertain -> drop.
        assert parse_verdict_json("model waffled").supported is False
        assert parse_verdict_json('{"evidence": "no verdict key"}').supported is False


class TestBuildVerifyPrompt:
    def test_contains_claim_and_code(self) -> None:
        prompt = build_verify_prompt(_triple(), "class IngestionPipeline: self.embedder")
        assert "IngestionPipeline" in prompt
        assert "uses" in prompt
        assert "EmbeddingClient" in prompt
        assert "self.embedder" in prompt  # the code
        assert "{{" not in prompt


class TestVerifyTriple:
    def test_supported_verdict(self) -> None:
        client = _FakeClient('{"supported": true, "evidence": "embed loop"}')
        verdict = verify_triple(_triple(), "code", client, "verify-model")
        assert verdict.supported is True
        assert verdict.evidence == "embed loop"


class TestVerifyAll:
    def test_keeps_only_supported_edges(self) -> None:
        supported = _triple("a.md")
        unsupported = Triple("A", "calls", "B", derived_from="b.md")
        client = _FakeClient('{"supported": true}', '{"supported": false}')
        kept = verify_all(
            [supported, unsupported],
            code_by_path={"a.md": "code a", "b.md": "code b"},
            client=client,
            model="verify-model",
        )
        assert kept == [supported]

    def test_drops_edge_with_no_available_code(self) -> None:
        # If the derived_from code is missing, the edge cannot be verified -> drop.
        client = _FakeClient('{"supported": true}')
        kept = verify_all([_triple("missing.md")], code_by_path={}, client=client, model="m")
        assert kept == []
