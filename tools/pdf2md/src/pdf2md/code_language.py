"""Heuristic source-language classification for fenced code blocks.

PDF extraction yields code with no language hint, but a language-tagged fence
(```` ```java ````) is materially better for AI/RAG ingestion: it preserves the
code-vs-prose signal and lets downstream tools highlight and parse correctly.

:func:`detect_language` scores a code snippet against per-language signal
patterns and returns the best match, or a caller-supplied *default* when no
signal is strong enough.  The classifier is intentionally conservative — it
prefers returning the default (or ``None``) over guessing wrong.
"""
from __future__ import annotations

import re

# Each language maps to a list of signal patterns. A snippet's score for a
# language is the number of distinct patterns it matches; the highest score
# wins. Ties are broken by the order of this dict (more specific formats first).
_SIGNALS: dict[str, list[re.Pattern[str]]] = {
    "http": [
        re.compile(r"^(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)\s+\S+\s+HTTP/\d", re.M),
        re.compile(r"^HTTP/\d\.\d\s+\d{3}", re.M),
    ],
    "xml": [
        re.compile(r"<\?xml\b"),
        re.compile(r"<!DOCTYPE\b", re.I),
        re.compile(r"</[A-Za-z][\w:-]*>"),
        re.compile(r"<[A-Za-z][\w:-]*(?:\s+[\w:-]+=\"[^\"]*\")*\s*/?>"),
    ],
    # JSON is identified by quoted-key/value structure, NOT by braces alone —
    # a bare "}" would otherwise mis-tag Java/JS fragments that end a block.
    "json": [
        re.compile(r"\"[\w.-]+\"\s*:\s*"),
        re.compile(r":\s*(\".*?\"|-?\d+(?:\.\d+)?|true|false|null)\s*[,}\]]?\s*$", re.M),
    ],
    "yaml": [
        re.compile(r"^---\s*$", re.M),
        re.compile(r"^\s*[\w.-]+:(?:\s|$)", re.M),
        re.compile(r"^\s*-\s+\S", re.M),
        re.compile(r"^(apiVersion|kind|metadata|spec):", re.M),
    ],
    "sql": [
        re.compile(r"\bCREATE\s+(TABLE|INDEX|VIEW|DATABASE|USER)\b", re.I),
        re.compile(r"\bINSERT\s+INTO\b", re.I),
        re.compile(r"\bSELECT\b[\s\S]*\bFROM\b", re.I),
        re.compile(r"\bUPDATE\b[\s\S]*\bSET\b", re.I),
        re.compile(r"\bDELETE\s+FROM\b", re.I),
        re.compile(r"\b(PRIMARY|FOREIGN)\s+KEY\b", re.I),
        re.compile(r"\bGRANT\b.*\bTO\b", re.I),
    ],
    "python": [
        re.compile(r"^#!.*\bpython", re.M),
        re.compile(r"\bdef\s+\w+\s*\("),
        re.compile(r"^\s*(from\s+[\w.]+\s+import|import\s+\w+)\s*$", re.M),
        re.compile(r"\bprint\("),
        re.compile(r"\b(elif|self|None|True|False)\b"),
        re.compile(r"__\w+__"),
    ],
    "java": [
        re.compile(r"\bpublic\s+(class|interface|enum|static|final|void)\b"),
        re.compile(r"\bpackage\s+[\w.]+;"),
        re.compile(r"\bimport\s+(java|javax|org|com)\.[\w.]+;"),
        re.compile(r"\bSystem\.(out|err)\."),
        re.compile(r"@Override\b"),
        re.compile(r"\b(String|int|boolean|var)\s+\w+\s*[=;]"),
        re.compile(r"\bnew\s+[A-Z]\w*\s*\("),
    ],
    "javascript": [
        re.compile(r"\b(const|let)\s+\w+\s*="),
        re.compile(r"=>"),
        re.compile(r"\bconsole\.(log|error)\("),
        re.compile(r"\brequire\(\s*['\"]"),
        re.compile(r"\bexport\s+(default|const|function)\b"),
    ],
    "bash": [
        re.compile(r"^#!.*\b(sh|bash|zsh)\b", re.M),
        re.compile(r"^\s*\$\s+\S", re.M),
        re.compile(
            r"^\s*(mvn|curl|wget|cd|npm|npx|git|sudo|export|docker|kubectl|"
            r"apt|apt-get|brew|chmod|chown|openssl|keytool|java\s+-jar|gradle)\b",
            re.M,
        ),
    ],
}

# A bare fence has nothing (but optional whitespace) after the opening backticks.
_BARE_FENCE_RE = re.compile(r"```[ \t]*\r?\n(.*?)\r?\n```", re.DOTALL)


def detect_language(code: str, default: str | None = None) -> str | None:
    """Return the most likely language tag for *code*, or *default* if unsure.

    Scores *code* against each language's signal patterns and returns the
    highest-scoring language (ties broken by signal-table order). When nothing
    matches, returns *default* (which may be ``None``).
    """
    if not code or not code.strip():
        return default

    best_lang: str | None = None
    best_score = 0
    for lang, patterns in _SIGNALS.items():
        score = sum(1 for pat in patterns if pat.search(code))
        if score > best_score:
            best_score = score
            best_lang = lang

    return best_lang if best_score > 0 else default


def tag_bare_fences(markdown: str, default: str | None = None) -> str:
    """Add a language tag to every bare ```` ``` ```` fence in *markdown*.

    Used to enrich engine output that emits untagged fences (e.g. Docling).
    Fences that already carry a language are left untouched because the regex
    only matches an opening fence followed immediately by a newline.
    """

    def _repl(match: re.Match[str]) -> str:
        body = match.group(1)
        lang = detect_language(body, default=default)
        return f"```{lang}\n{body}\n```" if lang else match.group(0)

    return _BARE_FENCE_RE.sub(_repl, markdown)
