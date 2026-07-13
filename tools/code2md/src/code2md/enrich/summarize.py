"""Generate per-file enrichment docs: summary + questions + key symbols.

The model is the injectable dependency (``client``); everything else — prompt
assembly, defensive JSON parsing, and rendering — is deterministic and unit-tested
without a live model.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from code2md import __version__
from code2md.enrich.ollama_client import OllamaClient
from code2md.enrich.scandoc import ParsedScanDoc

_PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "summarize.txt"


@dataclass
class Symbol:
    name: str
    description: str


@dataclass
class Enrichment:
    summary: str
    questions: list[str] = field(default_factory=list)
    symbols: list[Symbol] = field(default_factory=list)


def _load_prompt_template() -> str:
    return _PROMPT_PATH.read_text(encoding="utf-8")


def build_prompt(doc: ParsedScanDoc) -> str:
    # Token replacement (not str.format) because code bodies contain braces.
    template = _load_prompt_template()
    return (
        template.replace("{{PATH}}", doc.path)
        .replace("{{LANGUAGE}}", doc.language)
        .replace("{{CODE}}", doc.code)
    )


def parse_model_json(text: str) -> Enrichment:
    """Parse the model's JSON defensively.

    Falls back to treating the whole response as the summary so a mis-formatted
    reply degrades to a usable (if plain) enrichment instead of failing the run.
    """
    try:
        data = json.loads(text)
    except ValueError:
        return Enrichment(summary=text.strip())
    if not isinstance(data, dict):
        return Enrichment(summary=text.strip())

    summary = str(data.get("summary", "")).strip()
    questions = [str(q).strip() for q in data.get("questions", []) if str(q).strip()]
    symbols: list[Symbol] = []
    for item in data.get("symbols", []):
        if isinstance(item, dict) and item.get("name"):
            symbols.append(
                Symbol(
                    name=str(item["name"]).strip(),
                    description=str(item.get("description", "")).strip(),
                )
            )
    return Enrichment(summary=summary, questions=questions, symbols=symbols)


def summarize_document(doc: ParsedScanDoc, client: OllamaClient, model: str) -> Enrichment:
    raw = client.generate(model, build_prompt(doc), json_format=True)
    return parse_model_json(raw)


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def render_enriched_doc(
    doc: ParsedScanDoc, enrichment: Enrichment, model: str, generated_at: str | None = None
) -> str:
    lines = [
        "---",
        f"source: {doc.source}",
        f"path: _enriched/{doc.path}.enriched.md",
        f"derived_from: {doc.rel_doc_path.as_posix()}",
        "generated: true",
        f"model: {model}",
        f"generated_at: {generated_at or _now_iso()}",
        f"tool: code2md/{__version__}",
        "kind: file-summary",
        "---",
        "",
        f"# {doc.path}",
        "",
        "## Summary",
        "",
        enrichment.summary or "(no summary produced)",
    ]
    if enrichment.questions:
        lines += ["", "## Questions this file answers", ""]
        lines += [f"- {q}" for q in enrichment.questions]
    if enrichment.symbols:
        lines += ["", "## Key symbols", ""]
        lines += [f"- `{s.name}` — {s.description}".rstrip(" —") for s in enrichment.symbols]
    return "\n".join(lines) + "\n"


def iter_enrichable_docs(scan_dir: Path) -> list[Path]:
    """Return the scan documents eligible for enrichment.

    Excludes the mechanical overview, already-generated docs, and the ``_enriched/``
    subtree itself. Sorted for deterministic ordering.
    """
    docs: list[Path] = []
    for path in scan_dir.rglob("*.md"):
        rel = path.relative_to(scan_dir).as_posix()
        if rel.startswith("_enriched/") or rel.endswith(".enriched.md"):
            continue
        if path.name in {"_overview.md", "_architecture.md"}:
            continue
        docs.append(path)
    return sorted(docs, key=lambda p: p.as_posix())


def enriched_output_path(scan_dir: Path, doc: ParsedScanDoc) -> Path:
    rel = doc.rel_doc_path.as_posix()
    if rel.endswith(".md"):
        rel = rel[: -len(".md")]
    return scan_dir / "_enriched" / (rel + ".enriched.md")


def write_enriched(scan_dir: Path, doc: ParsedScanDoc, content: str) -> Path:
    out_path = enriched_output_path(scan_dir, doc)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content, encoding="utf-8")
    return out_path
