# <AI-Generated START>
"""Eval case model and dataset loading.

A case is one prompt + one scorer spec. Datasets are JSONL (one case per line) so they
version cleanly alongside model/prompt changes.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Case:
    id: str
    category: str
    scorer: dict
    prompt: str | None = None
    messages: list[dict] | None = None
    tools: list[dict] | None = None
    reference: str | None = None
    tags: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.messages is None:
            if self.prompt is None:
                raise ValueError(f"case {self.id!r} needs either 'prompt' or 'messages'")
            self.messages = [{"role": "user", "content": self.prompt}]

    @property
    def user_prompt(self) -> str:
        """The last user message content — used as the judge's 'prompt' context."""
        for msg in reversed(self.messages or []):
            if msg.get("role") == "user":
                return msg.get("content", "")
        return ""

    @classmethod
    def from_dict(cls, data: dict) -> Case:
        return cls(
            id=data["id"],
            category=data["category"],
            scorer=data["scorer"],
            prompt=data.get("prompt"),
            messages=data.get("messages"),
            tools=data.get("tools"),
            reference=data.get("reference"),
            tags=data.get("tags", []),
        )


def load_cases(path: str | Path) -> list[Case]:
    cases: list[Case] = []
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        cases.append(Case.from_dict(json.loads(line)))
    return cases
# <AI-Generated END>
