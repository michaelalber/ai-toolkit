"""Phase 3 — concept-graph relationship extraction (data model + validation).

Generates the ``A → verb → B`` triples that grounded-code-mcp's concept graph
consumes. The controlled vocabularies below are **vendored** from grounded's
``graph/graph_store.py`` (the two projects are separate repos, so there is no
import path). Keep them in sync: an extracted verb is normalised exactly the way
grounded's ``graph_builder`` normalises it, and any verb not in VALID_RELATIONS is
silently dropped by that parser — so we validate here and never emit a dead edge.

The model is the injectable dependency elsewhere; this module is pure and
unit-tested without a live model.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from code2md import __version__
from code2md.enrich.ollama_client import OllamaClient
from code2md.enrich.scandoc import ParsedScanDoc

_PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "relationships.txt"

# --- Vendored from grounded-code-mcp graph/graph_store.py (keep in sync) -------

VALID_DOMAINS: frozenset[str] = frozenset(
    {
        "testing",
        "dotnet",
        "python",
        "rust",
        "databases",
        "api-design",
        "edge-ai",
        "automation",
        "architecture",
        "security",
        "javascript",
        "ui-ux",
        "systems-thinking",
        "robotics",
        "php",
    }
)

VALID_TYPES: frozenset[str] = frozenset(
    {
        "pattern",
        "principle",
        "practice",
        "anti-pattern",
    }
)

VALID_RELATIONS: frozenset[str] = frozenset(
    {
        # Original abstract relations
        "alternative-to",
        "causes",
        "conflicts-with",
        "depends-on",
        "enables",
        "improves",
        "is-an-example-of",
        "prevents",
        "replaces",
        "requires",
        # Structural / architectural relations
        "bootstraps",
        "composes-with",
        "composed-by",
        "contains",
        "disables",
        "enforces",
        "extends",
        "governs",
        "guards",
        "implements",
        "integrates-with",
        "manages",
        "maps",
        "maps-to",
        "orchestrates",
        "separates",
        "supports",
        "transitions-to",
        # Data-flow / invocation relations
        "calls",
        "dispatched-after",
        "dispatched-via",
        "dispatches",
        "eager-loads",
        "listens-to",
        "loads",
        "polls",
        "produces",
        "projects",
        "propagates",
        "raises",
        "references",
        "registers",
        "resolves",
        "returns",
        "routes-to",
        "tracks",
        "transforms",
        "triggers",
        "uses",
        # Observability / quality relations
        "documents",
        "monitors",
        "reduces",
        "validates",
        # Persistence / configuration relations
        "caches",
        "collected-in",
        "configured-via",
        "configures",
        "consumes",
        "created-via",
        "exposes",
        "filtered-by",
        "has-flag",
        "has-lifetime",
        "has-state",
        "hooks",
        "implemented-via",
        "mapped-as",
        "may-contain",
        "may-own",
        "optionally-stored-in",
        "registered-as",
        "registered-in",
        "registered-via",
        "run-as",
        "stored-in",
        "stores",
        "updated-by",
        "wraps",
        "written-in",
        # Inverse / passive relations (from EF Core / gov lifecycle modelling)
        "applied-by",
        "applied-to",
        "bypassed-by",
        "caught-by",
        "caused-by",
        "differs-from",
        "enforces-invariants-via",
        "ensures",
        "generated-by",
        "materialized-by",
        "operates-on",
        "preferred-over",
        "prevented-by",
        "resolved-by",
        "suitable-for",
        "translated-by",
        "unsuitable-for",
    }
)

_DEFAULT_DOMAIN = "architecture"


@dataclass
class Triple:
    """One concept-graph edge extracted from a source file.

    ``derived_from`` is the scan document the edge came from — the citation the
    verification pass re-reads to confirm the edge, and the provenance pointer.
    """

    subject: str
    relation: str
    obj: str
    domain: str = _DEFAULT_DOMAIN
    node_type: str = ""
    description: str = ""
    derived_from: str = ""


def normalize_relation(raw: str) -> str | None:
    """Normalise a verb the way grounded's ``graph_builder`` does, or return None.

    Mirrors ``graph_builder._parse_triples``: collapse whitespace/underscores to
    hyphens and lowercase, then require membership in VALID_RELATIONS. Returning
    None lets callers drop the edge *before* it reaches (and is dropped by) the
    grounded parser.
    """
    normalized = re.sub(r"[\s_]+", "-", raw.strip()).lower()
    return normalized if normalized in VALID_RELATIONS else None


def parse_extraction_json(text: str, *, derived_from: str = "") -> list[Triple]:
    """Defensively parse the extraction model's JSON into valid Triples.

    Expects ``{"relationships": [{"subject", "relation", "object", "domain"?,
    "type"?, "description"?}, ...]}``. Silently drops any edge that is malformed,
    missing subject/object, or whose relation is not a valid verb. A completely
    unparseable response yields an empty list rather than raising.
    """
    try:
        data = json.loads(text)
    except ValueError:
        return []
    if not isinstance(data, dict):
        return []
    raw_edges = data.get("relationships")
    if not isinstance(raw_edges, list):
        return []

    triples: list[Triple] = []
    for item in raw_edges:
        if not isinstance(item, dict):
            continue
        subject = str(item.get("subject", "")).strip()
        obj = str(item.get("object", "")).strip()
        if not subject or not obj:
            continue
        relation = normalize_relation(str(item.get("relation", "")))
        if relation is None:
            continue
        raw_domain = str(item.get("domain", "")).strip()
        domain = raw_domain if raw_domain in VALID_DOMAINS else _DEFAULT_DOMAIN
        raw_type = str(item.get("type", "")).strip()
        node_type = raw_type if raw_type in VALID_TYPES else ""
        description = str(item.get("description", "")).strip()
        triples.append(
            Triple(
                subject=subject,
                relation=relation,
                obj=obj,
                domain=domain,
                node_type=node_type,
                description=description,
                derived_from=derived_from,
            )
        )
    return triples


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sanitize_concept(name: str) -> str:
    """Concept names are wrapped in double quotes in the triple format, so a stray
    quote would break parsing. Collapse quotes/whitespace to keep the line valid."""
    return re.sub(r"\s+", " ", name.replace('"', "'")).strip()


def _sanitize_bracket(text: str) -> str:
    """Bracket fields are ``[...]``-delimited, so a literal bracket in the field
    would close it early. Swap brackets for parentheses."""
    return re.sub(r"\s+", " ", text.replace("[", "(").replace("]", ")")).strip()


def _render_triple_line(triple: Triple, source_slug: str) -> str:
    # Bracket order fixed by grounded's parser: [source_slug] [domain] [type] [description]
    return (
        f'"{_sanitize_concept(triple.subject)}" → {triple.relation} → '
        f'"{_sanitize_concept(triple.obj)}" '
        f"[{source_slug}] [{triple.domain}] [{triple.node_type}] "
        f"[{_sanitize_bracket(triple.description)}]"
    )


def render_relationships(
    triples: list[Triple],
    project_slug: str,
    model: str,
    generated_at: str | None = None,
) -> str:
    """Render triples as a RELATIONSHIPS.md that grounded-code-mcp's graph builder
    parses. Triples are grouped under ``## … <!-- domain: X -->`` section headers
    (architecture first), and each carries an explicit ``[source_slug]`` guardrail.

    Front-matter is provenance only — grounded's parser ignores every non-arrow
    line, so it feeds the graph without being mistaken for a triple.
    """
    lines = [
        "---",
        "generated: true",
        f"model: {model}",
        f"generated_at: {generated_at or _now_iso()}",
        f"tool: code2md/{__version__}",
        "kind: concept-relationships",
        f"source: {project_slug}",
        "---",
        "",
        f"# Concept relationships for {project_slug}",
    ]

    by_domain: dict[str, list[Triple]] = {}
    for triple in triples:
        by_domain.setdefault(triple.domain, []).append(triple)

    # architecture first (structural spine), then remaining domains alphabetically.
    ordered = sorted(by_domain, key=lambda d: (d != _DEFAULT_DOMAIN, d))
    for domain in ordered:
        lines += ["", f"## {project_slug} — {domain}  <!-- domain: {domain} -->", ""]
        lines += [_render_triple_line(t, project_slug) for t in by_domain[domain]]

    return "\n".join(lines) + "\n"


def _load_prompt_template() -> str:
    return _PROMPT_PATH.read_text(encoding="utf-8")


def build_relationships_prompt(doc: ParsedScanDoc) -> str:
    """Assemble the extraction prompt for one scan document.

    Token replacement (not ``str.format``) because code bodies contain braces. The
    full controlled verb vocabulary is injected so the model can only pick valid
    verbs — anything else would be dropped by grounded's parser anyway.
    """
    template = _load_prompt_template()
    relations = ", ".join(sorted(VALID_RELATIONS))
    return (
        template.replace("{{PATH}}", doc.path)
        .replace("{{LANGUAGE}}", doc.language)
        .replace("{{RELATIONS}}", relations)
        .replace("{{CODE}}", doc.code)
    )


def extract_relationships(
    doc: ParsedScanDoc, client: OllamaClient, model: str
) -> list[Triple]:
    """Extract concept-graph triples this file participates in.

    Each triple is tagged with ``derived_from`` = the scan document, so the
    verification pass can re-read the exact code that must support the edge.
    """
    raw = client.generate(model, build_relationships_prompt(doc), json_format=True)
    return parse_extraction_json(raw, derived_from=doc.rel_doc_path.as_posix())
