"""Overview tests — README excerpt, language/module map, dependency parsing."""
from __future__ import annotations

from pathlib import Path

from code2md.overview import build_overview
from code2md.walker import iter_source_files


class TestBuildOverview:
    def test_includes_name_and_language_counts(self, sample_repo: Path) -> None:
        sources = iter_source_files(sample_repo)
        md = build_overview(sample_repo, "myapp", sources)
        assert "# myapp — codebase overview" in md
        assert "`python`" in md
        assert "`typescript`" in md

    def test_parses_pyproject_dependencies(self, sample_repo: Path) -> None:
        md = build_overview(sample_repo, "myapp", iter_source_files(sample_repo))
        assert "httpx>=0.27" in md
        assert "rich>=13" in md

    def test_includes_readme_excerpt(self, sample_repo: Path) -> None:
        md = build_overview(sample_repo, "myapp", iter_source_files(sample_repo))
        assert "A sample project." in md

    def test_is_prose_front_matter_not_code_fence(self, sample_repo: Path) -> None:
        md = build_overview(sample_repo, "myapp", iter_source_files(sample_repo))
        assert md.startswith("---")
        assert "path: _overview.md" in md
