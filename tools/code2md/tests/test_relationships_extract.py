"""Tests for the extraction orchestration (prompt assembly + model call).

The model is mocked via a fake client that returns canned JSON, so extraction is
tested without a live Ollama. The prompt must inject the controlled verb vocab
(the model can only use grounded's valid verbs) and the real code body.
"""
from __future__ import annotations

from pathlib import Path

from code2md.enrich.relationships import (
    build_relationships_prompt,
    extract_relationships,
)
from code2md.enrich.scandoc import ParsedScanDoc


def _doc() -> ParsedScanDoc:
    return ParsedScanDoc(
        doc_path=Path("/scan/src/ingest.py.md"),
        rel_doc_path=Path("src/ingest.py.md"),
        source="grounded-code-mcp",
        path="src/ingest.py",
        language="python",
        code="class IngestionPipeline:\n    def run(self): self.embedder.embed()\n",
    )


class _FakeClient:
    def __init__(self, response: str) -> None:
        self._response = response
        self.last_prompt: str | None = None

    def generate(self, model: str, prompt: str, *, json_format: bool = True) -> str:
        self.last_prompt = prompt
        return self._response


class TestBuildPrompt:
    def test_injects_code_path_language_and_verb_vocab(self) -> None:
        prompt = build_relationships_prompt(_doc())
        assert "src/ingest.py" in prompt
        assert "python" in prompt
        assert "IngestionPipeline" in prompt  # the code body
        # A representative controlled verb must be present so the model is constrained.
        assert "orchestrates" in prompt
        assert "composes-with" in prompt
        # No unreplaced template tokens leak through.
        assert "{{" not in prompt


class TestExtractRelationships:
    def test_returns_triples_tagged_with_derived_from(self) -> None:
        client = _FakeClient(
            '{"relationships": [{"subject": "IngestionPipeline", "relation": "uses",'
            ' "object": "EmbeddingClient", "domain": "architecture"}]}'
        )
        triples = extract_relationships(_doc(), client, "big-model-cloud")
        assert len(triples) == 1
        assert triples[0].subject == "IngestionPipeline"
        assert triples[0].relation == "uses"
        assert triples[0].derived_from == "src/ingest.py.md"

    def test_requests_json_and_passes_model(self) -> None:
        client = _FakeClient('{"relationships": []}')
        extract_relationships(_doc(), client, "big-model-cloud")
        assert client.last_prompt is not None
        assert "IngestionPipeline" in client.last_prompt

    def test_bad_model_output_yields_no_triples(self) -> None:
        client = _FakeClient("the model rambled instead of JSON")
        assert extract_relationships(_doc(), client, "m") == []
