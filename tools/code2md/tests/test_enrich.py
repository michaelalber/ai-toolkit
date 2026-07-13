"""Unit tests for the enrichment modules (no live model)."""
from __future__ import annotations

from pathlib import Path

from code2md.enrich.cache import EnrichCache
from code2md.enrich.scandoc import parse_scan_doc
from code2md.enrich.summarize import (
    Enrichment,
    Symbol,
    build_prompt,
    enriched_output_path,
    iter_enrichable_docs,
    parse_model_json,
    render_enriched_doc,
)

_SCAN_DOC = """---
source: myapp
path: src/main.py
language: python
tool: code2md/0.2.0
---

# src/main.py

```python
def greet(name):
    return f"hi {name}"
```
"""


def _write_scan_doc(scan_dir: Path, rel: str, text: str = _SCAN_DOC) -> Path:
    p = scan_dir / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


class TestScanDoc:
    def test_parses_front_matter_and_code(self, tmp_path: Path) -> None:
        doc_path = _write_scan_doc(tmp_path, "src/main.py.md")
        parsed = parse_scan_doc(doc_path, tmp_path)
        assert parsed.source == "myapp"
        assert parsed.path == "src/main.py"
        assert parsed.language == "python"
        assert "def greet(name):" in parsed.code
        assert parsed.rel_doc_path.as_posix() == "src/main.py.md"

    def test_handles_longer_fence(self, tmp_path: Path) -> None:
        text = _SCAN_DOC.replace("```python", "````python").replace("```\n", "````\n")
        doc_path = _write_scan_doc(tmp_path, "a.py.md", text)
        parsed = parse_scan_doc(doc_path, tmp_path)
        assert "def greet" in parsed.code

    def test_code_sha_is_stable(self, tmp_path: Path) -> None:
        p = _write_scan_doc(tmp_path, "a.py.md")
        assert parse_scan_doc(p, tmp_path).code_sha256 == parse_scan_doc(p, tmp_path).code_sha256


class TestParseModelJson:
    def test_valid(self) -> None:
        out = parse_model_json(
            '{"summary":"S","questions":["Q1"],"symbols":[{"name":"f","description":"d"}]}'
        )
        assert out.summary == "S"
        assert out.questions == ["Q1"]
        assert out.symbols[0].name == "f"

    def test_invalid_falls_back_to_summary(self) -> None:
        out = parse_model_json("not json at all")
        assert out.summary == "not json at all"
        assert out.questions == []

    def test_partial_json_is_tolerated(self) -> None:
        out = parse_model_json('{"summary":"only summary"}')
        assert out.summary == "only summary"
        assert out.symbols == []


class TestRender:
    def test_provenance_and_sections(self, tmp_path: Path) -> None:
        doc = parse_scan_doc(_write_scan_doc(tmp_path, "src/main.py.md"), tmp_path)
        enrichment = Enrichment(
            summary="Greets a user.",
            questions=["How to greet?"],
            symbols=[Symbol(name="greet", description="returns a greeting")],
        )
        md = render_enriched_doc(
            doc, enrichment, "qwen3-coder:30b", generated_at="2026-07-06T00:00:00Z"
        )
        assert md.startswith("---")
        assert "generated: true" in md
        assert "model: qwen3-coder:30b" in md
        assert "derived_from: src/main.py.md" in md
        assert "## Questions this file answers" in md
        assert "- `greet` — returns a greeting" in md

    def test_prose_only_no_code_fence(self, tmp_path: Path) -> None:
        # Enriched docs must ingest as prose (is_code=False), so no fenced blocks.
        doc = parse_scan_doc(_write_scan_doc(tmp_path, "a.py.md"), tmp_path)
        md = render_enriched_doc(doc, Enrichment(summary="s"), "m")
        assert "```" not in md


class TestPromptAndPaths:
    def test_build_prompt_injects_and_survives_braces(self, tmp_path: Path) -> None:
        doc = parse_scan_doc(_write_scan_doc(tmp_path, "a.py.md"), tmp_path)
        prompt = build_prompt(doc)  # code contains f"hi {name}" — braces must not break it
        assert "src/main.py" in prompt
        assert 'f"hi {name}"' in prompt

    def test_enriched_output_path(self, tmp_path: Path) -> None:
        doc = parse_scan_doc(_write_scan_doc(tmp_path, "src/main.py.md"), tmp_path)
        out = enriched_output_path(tmp_path, doc)
        assert out == tmp_path / "_enriched" / "src" / "main.py.enriched.md"

    def test_iter_excludes_overview_and_enriched(self, tmp_path: Path) -> None:
        _write_scan_doc(tmp_path, "src/main.py.md")
        (tmp_path / "_overview.md").write_text("# overview", encoding="utf-8")
        (tmp_path / "_enriched").mkdir()
        (tmp_path / "_enriched" / "src").mkdir()
        (tmp_path / "_enriched" / "src" / "main.py.enriched.md").write_text("x", encoding="utf-8")
        docs = {p.relative_to(tmp_path).as_posix() for p in iter_enrichable_docs(tmp_path)}
        assert docs == {"src/main.py.md"}


class TestCache:
    def test_fresh_after_update(self, tmp_path: Path) -> None:
        doc = parse_scan_doc(_write_scan_doc(tmp_path, "a.py.md"), tmp_path)
        cache = EnrichCache.load(tmp_path)
        assert not cache.is_fresh(doc, "m")
        cache.update(doc, "m")
        assert cache.is_fresh(doc, "m")
        assert not cache.is_fresh(doc, "other-model")  # model change invalidates

    def test_persists_across_load(self, tmp_path: Path) -> None:
        doc = parse_scan_doc(_write_scan_doc(tmp_path, "a.py.md"), tmp_path)
        cache = EnrichCache.load(tmp_path)
        cache.update(doc, "m")
        cache.save()
        assert EnrichCache.load(tmp_path).is_fresh(doc, "m")
