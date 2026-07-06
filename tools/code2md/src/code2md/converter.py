"""Render a single source file into a language-tagged Markdown document.

Each document is one fenced code block plus YAML front-matter, laid out so
grounded-code-mcp's code-aware chunker keeps it atomic (or splits it on
function boundaries) and tags each chunk with the correct ``code_language``.
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

from code2md import __version__
from code2md.models import SourceFile

_BACKTICK_RUN = re.compile(r"`+")


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _fence_for(text: str) -> str:
    """Return a backtick fence longer than any backtick run inside ``text``.

    Guards against a source file that itself contains ```` ``` ```` from
    prematurely closing the block.
    """
    longest = max((len(run) for run in _BACKTICK_RUN.findall(text)), default=0)
    return "`" * max(3, longest + 1)


def build_front_matter(
    source_file: SourceFile, project_name: str, git_commit: str | None
) -> str:
    lines = [
        "---",
        f"source: {project_name}",
        f"path: {source_file.rel_path.as_posix()}",
        f"language: {source_file.language}",
        f"extracted_at: {_now_iso()}",
    ]
    if git_commit:
        lines.append(f"git_commit: {git_commit}")
    lines.append(f"tool: code2md/{__version__}")
    lines.append("---")
    return "\n".join(lines) + "\n\n"


def render_document(
    source_file: SourceFile,
    project_name: str,
    git_commit: str | None,
    code_text: str,
    metadata: bool = True,
) -> str:
    rel = source_file.rel_path.as_posix()
    fence = _fence_for(code_text)
    body = f"# {rel}\n\n{fence}{source_file.language}\n{code_text.rstrip(chr(10))}\n{fence}\n"
    if metadata:
        return build_front_matter(source_file, project_name, git_commit) + body
    return body


def convert_file(
    source_file: SourceFile,
    project_name: str,
    git_commit: str | None,
    metadata: bool = True,
) -> str:
    code_text = source_file.abs_path.read_text(encoding="utf-8", errors="replace")
    return render_document(source_file, project_name, git_commit, code_text, metadata)


def output_path_for(source_file: SourceFile, out_dir: Path) -> Path:
    """Mirror the repo tree under ``out_dir`` with a ``.md`` sidecar name.

    ``src/foo.py`` -> ``<out_dir>/src/foo.py.md`` (matches grounded-code-mcp's
    ``foo.pdf.md`` sidecar convention).
    """
    return out_dir / (source_file.rel_path.as_posix() + ".md")


def write_document(source_file: SourceFile, out_dir: Path, content: str) -> Path:
    out_path = output_path_for(source_file, out_dir)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content, encoding="utf-8")
    return out_path
