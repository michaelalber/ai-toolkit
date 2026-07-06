"""Enumerate a repository's source files, respecting ``.gitignore``.

Prefers ``git ls-files`` (which already honours ``.gitignore`` and surfaces the
real working set) when the target is a git repo; otherwise walks the tree and
applies ``.gitignore`` rules via ``pathspec``.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

from code2md.language import language_for
from code2md.models import SourceFile

# Directories never worth scanning, used only on the non-git fallback path.
_DEFAULT_EXCLUDES: frozenset[str] = frozenset(
    {
        ".git",
        "node_modules",
        ".venv",
        "venv",
        "__pycache__",
        "dist",
        "build",
        ".pytest_cache",
        ".ruff_cache",
        ".mypy_cache",
        ".idea",
        ".tox",
        "target",
        ".next",
    }
)


def git_commit(repo: Path) -> str | None:
    """Return the short HEAD commit hash, or ``None`` if unavailable."""
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return result.stdout.strip() if result.returncode == 0 else None


def _git_ls_files(repo: Path) -> list[Path] | None:
    """List tracked + untracked-not-ignored files via git, or ``None``."""
    if not (repo / ".git").exists():
        return None
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), "ls-files", "--cached", "--others", "--exclude-standard"],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    return [Path(line) for line in result.stdout.splitlines() if line.strip()]


def _load_gitignore(repo: Path):
    gitignore = repo / ".gitignore"
    if not gitignore.exists():
        return None
    import pathspec

    return pathspec.PathSpec.from_lines(
        "gitignore", gitignore.read_text(encoding="utf-8").splitlines()
    )


def _walk_files(repo: Path) -> list[Path]:
    """Fallback enumeration for non-git trees, honouring ``.gitignore``."""
    spec = _load_gitignore(repo)
    found: list[Path] = []
    for root, dirs, files in os.walk(repo):
        dirs[:] = [d for d in dirs if d not in _DEFAULT_EXCLUDES]
        for filename in files:
            rel = (Path(root) / filename).relative_to(repo)
            if spec is not None and spec.match_file(rel.as_posix()):
                continue
            found.append(rel)
    return found


def iter_source_files(repo: Path, max_file_kb: int = 512) -> list[SourceFile]:
    """Return the source files under ``repo`` selected for conversion.

    A file is selected when its extension maps to a known language, it is a
    regular file, and it is no larger than ``max_file_kb``. Results are sorted
    by POSIX path for deterministic output.
    """
    rel_paths = _git_ls_files(repo)
    if rel_paths is None:
        rel_paths = _walk_files(repo)

    max_bytes = max_file_kb * 1024
    selected: list[SourceFile] = []
    for rel in rel_paths:
        abs_path = repo / rel
        language = language_for(abs_path)
        if not language:
            continue
        if not abs_path.is_file():
            continue
        if abs_path.stat().st_size > max_bytes:
            continue
        selected.append(SourceFile(abs_path=abs_path, rel_path=rel, language=language))

    selected.sort(key=lambda sf: sf.rel_path.as_posix())
    return selected
