"""Parse a code2md scan document back into its front-matter + code body.

Enrichment consumes the scan output (not the original repo), so it must recover the
``path`` / ``language`` / ``source`` fields and the fenced code from each ``*.md``.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

_FENCE_CHARS = "`"


@dataclass
class ParsedScanDoc:
    doc_path: Path  # absolute path of the .md scan document
    rel_doc_path: Path  # scan document path relative to the scan dir
    source: str  # project name (front-matter `source:`)
    path: str  # original code file path (front-matter `path:`)
    language: str  # fence label
    code: str  # code body extracted from the fence

    @property
    def code_sha256(self) -> str:
        return hashlib.sha256(self.code.encode("utf-8")).hexdigest()


def _parse_front_matter(text: str) -> tuple[dict[str, str], str]:
    """Return (front-matter dict, body-after-front-matter)."""
    if not text.startswith("---"):
        return {}, text
    lines = text.splitlines(keepends=True)
    end = None
    for i in range(1, len(lines)):
        if lines[i].rstrip("\n") == "---":
            end = i
            break
    if end is None:
        return {}, text
    fm: dict[str, str] = {}
    for raw in lines[1:end]:
        line = raw.rstrip("\n")
        if ":" in line:
            key, _, value = line.partition(":")
            fm[key.strip()] = value.strip()
    return fm, "".join(lines[end + 1 :])


def _extract_fenced_code(body: str) -> str:
    """Extract the content of the first fenced code block in ``body``."""
    lines = body.splitlines()
    fence: str | None = None
    collected: list[str] = []
    for line in lines:
        stripped = line.strip()
        if fence is None:
            if stripped.startswith(_FENCE_CHARS * 3):
                fence = stripped[: len(stripped) - len(stripped.lstrip(_FENCE_CHARS))]
            continue
        # inside the block — a line of only the fence's backticks closes it
        if stripped == fence:
            break
        collected.append(line)
    return "\n".join(collected)


def parse_scan_doc(doc_path: Path, scan_dir: Path) -> ParsedScanDoc:
    text = doc_path.read_text(encoding="utf-8", errors="replace")
    fm, body = _parse_front_matter(text)
    return ParsedScanDoc(
        doc_path=doc_path,
        rel_doc_path=doc_path.relative_to(scan_dir),
        source=fm.get("source", ""),
        path=fm.get("path", doc_path.name),
        language=fm.get("language", ""),
        code=_extract_fenced_code(body),
    )
