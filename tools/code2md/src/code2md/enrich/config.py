from __future__ import annotations

import os
from dataclasses import dataclass

DEFAULT_OLLAMA_HOST = "http://localhost:11434"


@dataclass
class EnrichConfig:
    """Inputs for a `code2md enrich` run.

    ``model`` is required (no hardcoded default) per the project's AI/ML standard —
    models are deprecated without notice, so the name is always supplied explicitly
    via ``--model`` or the ``CODE2MD_ENRICH_MODEL`` env var.
    """

    scan_dir: "os.PathLike[str] | str"
    model: str
    ollama_host: str = DEFAULT_OLLAMA_HOST
    force: bool = False
    timeout_s: float = 180.0
    verbose: bool = False


def resolve_ollama_host(explicit: str | None) -> str:
    """CLI flag wins, then ``OLLAMA_HOST`` env, then localhost default."""
    return explicit or os.environ.get("OLLAMA_HOST") or DEFAULT_OLLAMA_HOST


def resolve_model(explicit: str | None) -> str | None:
    """CLI flag wins, then ``CODE2MD_ENRICH_MODEL`` env. May be ``None``."""
    return explicit or os.environ.get("CODE2MD_ENRICH_MODEL")
