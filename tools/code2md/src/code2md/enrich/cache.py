"""SHA-keyed enrichment cache — regenerate only changed files.

Keyed by (code SHA-256, model id) so a code change *or* a model change invalidates the
entry. Stored as a small JSON manifest inside the scan dir's ``_enriched/`` subtree.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from code2md.enrich.scandoc import ParsedScanDoc

_CACHE_NAME = "enrich-manifest.json"


@dataclass
class EnrichCache:
    path: Path
    entries: dict[str, dict[str, str]] = field(default_factory=dict)

    @classmethod
    def load(cls, scan_dir: Path) -> "EnrichCache":
        path = scan_dir / "_enriched" / _CACHE_NAME
        entries: dict[str, dict[str, str]] = {}
        if path.is_file():
            try:
                entries = json.loads(path.read_text(encoding="utf-8")).get("entries", {})
            except (OSError, ValueError):
                entries = {}
        return cls(path=path, entries=entries)

    def is_fresh(self, doc: ParsedScanDoc, model: str) -> bool:
        entry = self.entries.get(doc.rel_doc_path.as_posix())
        return bool(entry) and entry.get("sha256") == doc.code_sha256 and entry.get("model") == model

    def update(self, doc: ParsedScanDoc, model: str) -> None:
        self.entries[doc.rel_doc_path.as_posix()] = {"sha256": doc.code_sha256, "model": model}

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps({"entries": self.entries}, indent=2), encoding="utf-8")
