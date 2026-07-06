"""Walker tests — enumeration honours .gitignore and skips noise."""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

from code2md.walker import git_commit, iter_source_files


class TestFallbackWalk:
    def test_selects_source_and_respects_gitignore(self, sample_repo: Path) -> None:
        rel = {sf.rel_path.as_posix() for sf in iter_source_files(sample_repo)}
        assert "src/main.py" in rel
        assert "src/util.ts" in rel
        # Excluded by .gitignore / excluded dir / prose:
        assert "secret.py" not in rel
        assert "build/artifact.py" not in rel
        assert "README.md" not in rel

    def test_labels_are_assigned(self, sample_repo: Path) -> None:
        by_path = {sf.rel_path.as_posix(): sf.language for sf in iter_source_files(sample_repo)}
        assert by_path["src/main.py"] == "python"
        assert by_path["src/util.ts"] == "typescript"

    def test_skips_files_over_size_limit(self, sample_repo: Path) -> None:
        (sample_repo / "src" / "big.py").write_text("x = 0\n" * 5000, encoding="utf-8")
        rel = {sf.rel_path.as_posix() for sf in iter_source_files(sample_repo, max_file_kb=1)}
        assert "src/big.py" not in rel
        assert "src/main.py" in rel

    def test_results_are_sorted(self, sample_repo: Path) -> None:
        paths = [sf.rel_path.as_posix() for sf in iter_source_files(sample_repo)]
        assert paths == sorted(paths)


@pytest.mark.skipif(shutil.which("git") is None, reason="git not available")
class TestGitPath:
    def test_git_ls_files_respects_gitignore(self, sample_repo: Path) -> None:
        subprocess.run(["git", "init", "-q"], cwd=sample_repo, check=True)
        rel = {sf.rel_path.as_posix() for sf in iter_source_files(sample_repo)}
        assert "src/main.py" in rel
        assert "secret.py" not in rel  # ignored → not surfaced by git ls-files

    def test_git_commit_returns_hash(self, sample_repo: Path) -> None:
        env = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
        subprocess.run(["git", "init", "-q"], cwd=sample_repo, check=True)
        subprocess.run(["git", "add", "src/main.py"], cwd=sample_repo, check=True)
        subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=sample_repo, check=True, env={**env, "PATH": __import__("os").environ["PATH"]})
        assert git_commit(sample_repo)

    def test_git_commit_none_outside_repo(self, tmp_path: Path) -> None:
        assert git_commit(tmp_path) is None
