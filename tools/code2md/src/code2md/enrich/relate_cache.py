"""SHA-keyed cache for Phase 3 relationship extraction.

Like the Phase 1 enrich cache, keyed by (code SHA-256, model id) so a code or model
change invalidates the entry. Unlike Phase 1, it also **stores the verified triples**
per file: Phase 3 emits one aggregate RELATIONSHIPS.md, so a skipped (unchanged) file
still needs to contribute its edges to the rebuilt document.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

from code2md.enrich.relationships import Triple
from code2md.enrich.scandoc import ParsedScanDoc

_CACHE_NAME = "relate-manifest.json"


@dataclass
class RelateCache:
    path: Path
    entries: dict[str, dict] = field(default_factory=dict)

    @classmethod
    def load(cls, scan_dir: Path) -> "RelateCache":
        path = scan_dir / "_enriched" / _CACHE_NAME
        entries: dict[str, dict] = {}
        if path.is_file():
            try:
                entries = json.loads(path.read_text(encoding="utf-8")).get("entries", {})
            except (OSError, ValueError):
                entries = {}
        return cls(path=path, entries=entries)

    def is_fresh(self, doc: ParsedScanDoc, model: str) -> bool:
        entry = self.entries.get(doc.rel_doc_path.as_posix())
        return (
            bool(entry)
            and entry.get("sha256") == doc.code_sha256
            and entry.get("model") == model
        )

    def get_triples(self, doc: ParsedScanDoc) -> list[Triple]:
        entry = self.entries.get(doc.rel_doc_path.as_posix())
        if not entry:
            return []
        return [Triple(**t) for t in entry.get("triples", [])]

    def update(self, doc: ParsedScanDoc, model: str, triples: list[Triple]) -> None:
        self.entries[doc.rel_doc_path.as_posix()] = {
            "sha256": doc.code_sha256,
            "model": model,
            "triples": [asdict(t) for t in triples],
        }

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps({"entries": self.entries}, indent=2), encoding="utf-8")
