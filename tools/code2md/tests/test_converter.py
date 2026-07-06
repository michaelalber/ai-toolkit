"""Converter tests — front-matter, fence tagging, fence-safety, output paths."""
from __future__ import annotations

from pathlib import Path

from code2md.converter import (
    build_front_matter,
    convert_file,
    output_path_for,
    render_document,
)
from code2md.models import SourceFile


def _sf(tmp_path: Path, rel: str, language: str, text: str) -> SourceFile:
    abs_path = tmp_path / rel
    abs_path.parent.mkdir(parents=True, exist_ok=True)
    abs_path.write_text(text, encoding="utf-8")
    return SourceFile(abs_path=abs_path, rel_path=Path(rel), language=language)


class TestFrontMatter:
    def test_contains_path_language_source(self, tmp_path: Path) -> None:
        sf = _sf(tmp_path, "src/main.py", "python", "x = 1\n")
        fm = build_front_matter(sf, "myapp", "abc1234")
        assert "source: myapp" in fm
        assert "path: src/main.py" in fm
        assert "language: python" in fm
        assert "git_commit: abc1234" in fm

    def test_omits_git_commit_when_absent(self, tmp_path: Path) -> None:
        sf = _sf(tmp_path, "a.py", "python", "x = 1\n")
        assert "git_commit" not in build_front_matter(sf, "myapp", None)


class TestRender:
    def test_wraps_code_in_language_fence(self, tmp_path: Path) -> None:
        sf = _sf(tmp_path, "a.py", "python", "def f():\n    return 1\n")
        doc = convert_file(sf, "myapp", None)
        assert "```python\n" in doc
        assert "def f():" in doc

    def test_no_metadata_flag_omits_front_matter(self, tmp_path: Path) -> None:
        sf = _sf(tmp_path, "a.py", "python", "x = 1\n")
        doc = render_document(sf, "myapp", None, "x = 1\n", metadata=False)
        assert not doc.startswith("---")
        assert "```python" in doc

    def test_fence_safety_with_embedded_backticks(self, tmp_path: Path) -> None:
        # Source containing a triple-backtick run must get a longer outer fence.
        code = 'doc = """\n```\ncode\n```\n"""\n'
        sf = _sf(tmp_path, "a.py", "python", code)
        doc = render_document(sf, "myapp", None, code)
        assert "````python\n" in doc  # 4-backtick fence


class TestOutputPath:
    def test_mirrors_tree_with_md_suffix(self, tmp_path: Path) -> None:
        sf = _sf(tmp_path, "src/pkg/mod.py", "python", "x = 1\n")
        out = output_path_for(sf, Path("/out"))
        assert out == Path("/out/src/pkg/mod.py.md")
