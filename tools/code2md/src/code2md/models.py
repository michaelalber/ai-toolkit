from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ScanConfig:
    """Inputs for a single `code2md scan` run."""

    repo_path: Path
    out_dir: Path
    name: str
    overview: bool = True
    metadata: bool = True
    max_file_kb: int = 512
    verbose: bool = False


@dataclass
class SourceFile:
    """A source file selected for conversion."""

    abs_path: Path
    rel_path: Path  # relative to the repo root
    language: str  # fence label; always a known language for selected files


def slugify_name(raw: str) -> str:
    """Normalise a project name into grounded-code-mcp's canonical slug form.

    The scan output directory name doubles as the chunk ``source_path`` prefix
    and the concept-graph ``source_slug`` in grounded-code-mcp. Graph expansion
    matches a slugified ``source_slug`` against ``source_path`` verbatim, so the
    directory name must already be in grounded's hyphenated form — i.e. this must
    mirror ``graph_store.slugify()`` exactly and be idempotent under it.

    ``My App`` -> ``my-app``; ``grounded_code_mcp`` -> ``grounded-code-mcp``.
    """
    text = raw.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-") or "project"


def collection_suffix(slug: str) -> str:
    """Collection-name suffix for a project slug (underscore convention).

    Qdrant collections in grounded-code-mcp use underscores (``grounded_internal``,
    ``grounded_api_design``), so a hyphenated project slug maps to an underscored
    collection: ``my-app`` -> ``project_my_app`` (server prepends ``grounded_``).
    """
    return "project_" + slug.replace("-", "_")
