# <AI-Generated START>
"""The finding model.

A rule emits ``Finding``s; nothing else. Severity decides the exit code, ``evals_tc``
records which ``evals.md`` test case the rule automates so the mapping stays auditable in
both directions, and ``file``/``line`` make every finding clickable.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class Severity(Enum):
    ERROR = "error"
    WARNING = "warning"

    def __lt__(self, other: Severity) -> bool:
        order = [Severity.ERROR, Severity.WARNING]
        return order.index(self) < order.index(other)


@dataclass(frozen=True)
class Finding:
    rule_id: str
    severity: Severity
    message: str
    skill: str | None = None
    file: Path | None = None
    line: int | None = None
    evals_tc: str | None = None

    @property
    def location(self) -> str:
        if self.file is None:
            return self.skill or "<repo>"
        return f"{self.file}:{self.line}" if self.line else str(self.file)

    def key(self) -> tuple:
        """Identity for baseline matching.

        Excludes the line number, so a finding does not silently un-baseline itself when
        unrelated edits shift it down a few lines. Excludes the path too: it is absolute
        at runtime but stored relative, and rule + skill + message already identifies a
        finding uniquely (repo-scoped rules name their file in the message).
        """
        return (self.rule_id, self.skill, self.message)


@dataclass
class FindingSet:
    findings: list[Finding] = field(default_factory=list)

    def add(self, finding: Finding) -> None:
        self.findings.append(finding)

    def extend(self, findings) -> None:
        self.findings.extend(findings)

    def __len__(self) -> int:
        return len(self.findings)

    def __iter__(self):
        return iter(self.findings)

    @property
    def errors(self) -> list[Finding]:
        return [f for f in self.findings if f.severity is Severity.ERROR]

    @property
    def warnings(self) -> list[Finding]:
        return [f for f in self.findings if f.severity is Severity.WARNING]

    def by_rule(self) -> dict[str, list[Finding]]:
        out: dict[str, list[Finding]] = {}
        for finding in self.findings:
            out.setdefault(finding.rule_id, []).append(finding)
        return out

    def for_rule(self, rule_id: str) -> list[Finding]:
        return [f for f in self.findings if f.rule_id == rule_id]

    def for_skill(self, name: str) -> list[Finding]:
        return [f for f in self.findings if f.skill == name]

    def rule_counts(self) -> Counter:
        return Counter(f.rule_id for f in self.findings)

    def sorted(self) -> list[Finding]:
        """Errors first, then by rule id, then by location — a stable report order."""
        return sorted(
            self.findings,
            key=lambda f: (f.severity is Severity.WARNING, f.rule_id, f.skill or "", f.line or 0),
        )

    def without(self, keys: set[tuple]) -> FindingSet:
        """Drop findings whose ``key()`` is baselined."""
        return FindingSet([f for f in self.findings if f.key() not in keys])
# <AI-Generated END>
