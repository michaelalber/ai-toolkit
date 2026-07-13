"""Synthesize a prose ``_overview.md`` for a scanned repository.

Prose (not fenced code) so grounded-code-mcp ingests it as text chunks: it
gives an AI session a map of the project — README excerpt, module/language
breakdown, and declared dependencies — alongside the per-file code documents.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from code2md import __version__
from code2md.models import SourceFile

if sys.version_info >= (3, 11):
    import tomllib as _toml
else:  # pragma: no cover - exercised only on 3.10
    import tomli as _toml

_README_NAMES = ("README.md", "README.rst", "README.txt", "README")
_README_EXCERPT_CHARS = 1500


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_toml(path: Path) -> dict:
    try:
        with path.open("rb") as handle:
            return _toml.load(handle)
    except (OSError, ValueError):
        return {}


def _read_readme(repo: Path) -> str | None:
    for name in _README_NAMES:
        candidate = repo / name
        if candidate.is_file():
            text = candidate.read_text(encoding="utf-8", errors="replace").strip()
            if len(text) > _README_EXCERPT_CHARS:
                text = text[:_README_EXCERPT_CHARS].rstrip() + "\n\n… (truncated)"
            return text
    return None


def _dependencies(repo: Path) -> list[str]:
    """Collect declared dependencies from common manifests (best effort)."""
    deps: list[str] = []

    pyproject = repo / "pyproject.toml"
    if pyproject.is_file():
        data = _load_toml(pyproject)
        project = data.get("project", {})
        deps.extend(str(d) for d in project.get("dependencies", []))

    cargo = repo / "Cargo.toml"
    if cargo.is_file():
        data = _load_toml(cargo)
        deps.extend(str(name) for name in data.get("dependencies", {}))

    package_json = repo / "package.json"
    if package_json.is_file():
        try:
            data = json.loads(package_json.read_text(encoding="utf-8"))
            deps.extend(str(name) for name in data.get("dependencies", {}))
        except (OSError, ValueError):
            pass

    return deps


def _module_map(sources: list[SourceFile]) -> Counter[str]:
    """Count source files per top-level directory (``.`` for repo root)."""
    counts: Counter[str] = Counter()
    for source_file in sources:
        parts = source_file.rel_path.parts
        top = parts[0] if len(parts) > 1 else "."
        counts[top] += 1
    return counts


def build_overview(repo: Path, project_name: str, sources: list[SourceFile]) -> str:
    languages = Counter(sf.language for sf in sources)
    modules = _module_map(sources)
    readme = _read_readme(repo)
    deps = _dependencies(repo)

    lines = [
        "---",
        f"source: {project_name}",
        "path: _overview.md",
        f"extracted_at: {_now_iso()}",
        f"tool: code2md/{__version__}",
        "---",
        "",
        f"# {project_name} — codebase overview",
        "",
        f"Machine-generated snapshot of **{len(sources)}** source files "
        f"across **{len(languages)}** languages.",
        "",
        "## Languages",
        "",
    ]
    for language, count in languages.most_common():
        lines.append(f"- `{language}`: {count} file(s)")

    lines += ["", "## Modules", ""]
    for module, count in sorted(modules.items()):
        lines.append(f"- `{module}/`: {count} file(s)")

    lines += ["", "## Dependencies", ""]
    if deps:
        for dep in deps:
            lines.append(f"- {dep}")
    else:
        lines.append("- (none declared or manifest not recognised)")

    if readme:
        lines += ["", "## README excerpt", "", readme]

    return "\n".join(lines) + "\n"


def write_overview(out_dir: Path, content: str) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "_overview.md"
    out_path.write_text(content, encoding="utf-8")
    return out_path
