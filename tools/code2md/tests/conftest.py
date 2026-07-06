"""Shared fixtures for code2md tests."""
from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def sample_repo(tmp_path: Path) -> Path:
    """A non-git project tree with a .gitignore, source, prose, and noise."""
    repo = tmp_path / "myapp"
    (repo / "src").mkdir(parents=True)
    (repo / "build").mkdir()

    (repo / "src" / "main.py").write_text(
        "def greet(name):\n    return f'hi {name}'\n", encoding="utf-8"
    )
    (repo / "src" / "util.ts").write_text(
        "export function add(a: number, b: number) { return a + b }\n", encoding="utf-8"
    )
    (repo / "README.md").write_text("# MyApp\n\nA sample project.\n", encoding="utf-8")
    (repo / "pyproject.toml").write_text(
        '[project]\nname = "myapp"\ndependencies = ["httpx>=0.27", "rich>=13"]\n',
        encoding="utf-8",
    )
    # Noise that must be excluded:
    (repo / ".gitignore").write_text("secret.py\nbuild/\n", encoding="utf-8")
    (repo / "secret.py").write_text("TOKEN = 'nope'\n", encoding="utf-8")
    (repo / "build" / "artifact.py").write_text("x = 1\n", encoding="utf-8")

    return repo
