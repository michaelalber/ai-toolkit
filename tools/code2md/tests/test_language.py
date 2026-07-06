"""Language-mapping tests — the KNOWN_LANGUAGES subset check is the key gate."""
from __future__ import annotations

from pathlib import Path

from code2md.language import EXTENSION_LANGUAGE, KNOWN_LANGUAGES, language_for


class TestSubsetInvariant:
    def test_all_labels_are_known_languages(self) -> None:
        # Every emitted fence label must be recognised by grounded-code-mcp,
        # else search_code_examples(language=...) silently drops it.
        assert set(EXTENSION_LANGUAGE.values()) <= KNOWN_LANGUAGES


class TestLanguageFor:
    def test_common_extensions(self) -> None:
        assert language_for(Path("a/main.py")) == "python"
        assert language_for(Path("Service.cs")) == "csharp"
        assert language_for(Path("app.ts")) == "typescript"
        assert language_for(Path("lib.rs")) == "rust"

    def test_case_insensitive(self) -> None:
        assert language_for(Path("MAIN.PY")) == "python"

    def test_unknown_extension_returns_empty(self) -> None:
        assert language_for(Path("data.xyz")) == ""

    def test_prose_extensions_excluded(self) -> None:
        # Prose is intentionally unmapped (handled by the overview instead).
        assert language_for(Path("README.md")) == ""
        assert language_for(Path("notes.txt")) == ""
