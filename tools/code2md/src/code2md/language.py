"""Map source-file extensions to Markdown fence labels.

The fence label is the *only* thing that makes grounded-code-mcp treat an
emitted block as code: its chunker splits large blocks on function boundaries
by matching the fence label (``FUNCTION_PATTERNS`` in ``chunking.py``), and
``search_code_examples(language=...)`` filters on the ``code_language`` payload
against a fixed allowlist.

Every value in ``EXTENSION_LANGUAGE`` MUST therefore stay a subset of
``KNOWN_LANGUAGES`` below, which mirrors grounded-code-mcp's frozenset
(``src/grounded_code_mcp/server.py`` lines 34-61). ``tests/test_language.py``
enforces the subset invariant so drift is caught in review.
"""
from __future__ import annotations

from pathlib import Path

# Mirror of grounded-code-mcp server.py:34-61 (KNOWN_LANGUAGES). Keep in sync.
KNOWN_LANGUAGES: frozenset[str] = frozenset(
    {
        "python",
        "csharp",
        "javascript",
        "typescript",
        "java",
        "go",
        "rust",
        "cpp",
        "c",
        "sql",
        "bash",
        "shell",
        "yaml",
        "json",
        "html",
        "css",
        "markdown",
        "php",
        "ruby",
        "scala",
        "kotlin",
        "swift",
        "r",
        "text",
    }
)

# Only real source-code extensions are mapped; prose (.md/.rst/.txt) and pure
# data/config (.json/.yaml/.toml) are intentionally excluded from per-file
# conversion — README and dependency manifests flow into the overview instead.
EXTENSION_LANGUAGE: dict[str, str] = {
    ".py": "python",
    ".pyi": "python",
    ".cs": "csharp",
    ".js": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".java": "java",
    ".go": "go",
    ".rs": "rust",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".cxx": "cpp",
    ".hpp": "cpp",
    ".hh": "cpp",
    ".c": "c",
    ".h": "c",
    ".php": "php",
    ".rb": "ruby",
    ".scala": "scala",
    ".kt": "kotlin",
    ".kts": "kotlin",
    ".swift": "swift",
    ".r": "r",
    ".sql": "sql",
    ".sh": "bash",
    ".bash": "bash",
    ".html": "html",
    ".htm": "html",
    ".css": "css",
}


def language_for(path: Path) -> str:
    """Return the fence label for ``path`` (extension match, case-insensitive).

    Returns ``""`` for extensions that are not mapped source code — the walker
    treats an empty label as "not a source file" and skips it.
    """
    return EXTENSION_LANGUAGE.get(path.suffix.lower(), "")
