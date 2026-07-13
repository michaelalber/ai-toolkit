"""Phase 3 edge verification — the guard against hallucinated routing.

A false relationship is the one place generation can corrupt retrieval invisibly
(it injects a false *routing* decision, steering the runtime model to real-but-
irrelevant code). So every extracted triple is re-checked against the exact code it
was derived from, and dropped unless the code clearly supports it. Verdicts are
conservative: anything unparseable or ambiguous is treated as unsupported.

The model is the injectable dependency (``client``); prompt assembly and parsing are
deterministic and unit-tested without a live model.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from code2md.enrich.ollama_client import OllamaClient
from code2md.enrich.relationships import Triple

_PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "verify_edge.txt"


@dataclass
class Verdict:
    supported: bool
    evidence: str = ""


def _load_prompt_template() -> str:
    return _PROMPT_PATH.read_text(encoding="utf-8")


def build_verify_prompt(triple: Triple, code: str) -> str:
    # Token replacement (not str.format) because code bodies contain braces.
    template = _load_prompt_template()
    return (
        template.replace("{{SUBJECT}}", triple.subject)
        .replace("{{RELATION}}", triple.relation)
        .replace("{{OBJECT}}", triple.obj)
        .replace("{{PATH}}", triple.derived_from)
        .replace("{{CODE}}", code)
    )


def parse_verdict_json(text: str) -> Verdict:
    """Parse the verifier's JSON conservatively.

    A response that is not valid JSON, not an object, or missing an explicit
    truthy ``supported`` is treated as *unsupported* — uncertain edges are dropped.
    """
    try:
        data = json.loads(text)
    except ValueError:
        return Verdict(False)
    if not isinstance(data, dict):
        return Verdict(False)
    supported = data.get("supported") is True
    evidence = str(data.get("evidence", "")).strip()
    return Verdict(supported, evidence)


def verify_triple(triple: Triple, code: str, client: OllamaClient, model: str) -> Verdict:
    raw = client.generate(model, build_verify_prompt(triple, code), json_format=True)
    return parse_verdict_json(raw)


def verify_all(
    triples: list[Triple],
    code_by_path: dict[str, str],
    client: OllamaClient,
    model: str,
) -> list[Triple]:
    """Return only the triples whose derived-from code supports them.

    A triple whose ``derived_from`` code is unavailable cannot be verified and is
    dropped — verification is required, so an unverifiable edge never ships.
    """
    kept: list[Triple] = []
    for triple in triples:
        code = code_by_path.get(triple.derived_from)
        if not code:
            continue
        if verify_triple(triple, code, client, model).supported:
            kept.append(triple)
    return kept
