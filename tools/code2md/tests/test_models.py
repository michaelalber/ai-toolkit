"""Tests for project-name slugification.

The scan output directory name doubles as the chunk ``source_path`` prefix in
grounded-code-mcp and as the concept-graph ``source_slug``. grounded's graph
builder runs every ``source_slug`` through its own ``slugify()`` (hyphen form),
while the match in ``search_knowledge`` is a verbatim ``source_path.startswith``.
So the directory name must already BE in grounded's canonical hyphen form for
graph expansion to resolve — i.e. code2md's slug must mirror grounded's slugify
exactly and be idempotent under it.
"""
from __future__ import annotations

import re

import pytest

from code2md.models import collection_suffix, slugify_name


def _grounded_slugify(text: str) -> str:
    """A copy of grounded-code-mcp's graph_store.slugify() — the canonical form
    code2md must produce so ``slugify(dirname) == dirname``."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")


class TestSlugifyName:
    @pytest.mark.parametrize(
        ("raw", "expected"),
        [
            ("My App", "my-app"),
            ("grounded_code_mcp", "grounded-code-mcp"),
            ("grounded-code-mcp", "grounded-code-mcp"),
            ("  Spaced  Name  ", "spaced-name"),
        ],
    )
    def test_produces_hyphenated_slug(self, raw: str, expected: str) -> None:
        assert slugify_name(raw) == expected

    def test_empty_falls_back_to_project(self) -> None:
        assert slugify_name("   ") == "project"

    @pytest.mark.parametrize(
        "raw",
        ["My App", "grounded_code_mcp", "weird.name.v2", "a__b--c", "Café Project"],
    )
    def test_matches_grounded_slugify_and_is_idempotent(self, raw: str) -> None:
        slug = slugify_name(raw)
        # Directory name must survive grounded's slugify unchanged, else graph
        # expansion (source_slug prefix vs source_path) never matches.
        assert _grounded_slugify(slug) == slug
        assert _grounded_slugify(raw) == slug


class TestCollectionSuffix:
    @pytest.mark.parametrize(
        ("slug", "expected"),
        [
            ("my-app", "project_my_app"),
            ("grounded-code-mcp", "project_grounded_code_mcp"),
            ("myapp", "project_myapp"),
        ],
    )
    def test_underscore_collection_name(self, slug: str, expected: str) -> None:
        assert collection_suffix(slug) == expected
