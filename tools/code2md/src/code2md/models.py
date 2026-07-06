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
    """Normalise a project name into a collection-safe slug (``[a-z0-9_]``).

    ``My App`` -> ``my_app``; the grounded-code-mcp collection becomes
    ``project_my_app``.
    """
    slug = re.sub(r"[^0-9a-zA-Z]+", "_", raw.strip().lower())
    return slug.strip("_") or "project"
