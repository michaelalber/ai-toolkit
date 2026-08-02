# <AI-Generated START>
"""Parsing of ``skills/skill-creator/references/scoring-rubric.md``.

The rubric file stays the single source of truth — it is parsed at run time, not
transcribed here. Its sha256 goes into the run manifest, so editing the rubric explicitly
invalidates a scorecard baseline instead of silently shifting every number.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

RUBRIC_PATH = Path("skills/skill-creator/references/scoring-rubric.md")

_DIMENSION = re.compile(r"^##\s+Dimension\s+(\d+)\s*[—-]\s*(.+?)\s*$")
_SCORE_ROW = re.compile(r"^\|\s*([1-5])\s*\|\s*(.+?)\s*\|\s*$")
_THRESHOLD_ROW = re.compile(
    r"^\|\s*(?:(\d+)\s*[–-]\s*(\d+)|<\s*(\d+))\s*\|\s*([A-Z]+)\s*\|\s*(.+?)\s*\|\s*$"
)
_HEADING = re.compile(r"^#{1,6}\s")
_TABLE = re.compile(r"^\s*\|")

MAX_PER_DIMENSION = 5


@dataclass(frozen=True)
class Dimension:
    number: int
    name: str
    question: str
    criteria: dict[int, str]

    @property
    def key(self) -> str:
        return f"d{self.number}"

    def criteria_table(self) -> str:
        return "\n".join(f"{score}: {self.criteria[score]}" for score in sorted(self.criteria,
                                                                                reverse=True))


@dataclass(frozen=True)
class Threshold:
    low: int
    high: int
    verdict: str
    action: str


@dataclass(frozen=True)
class Rubric:
    dimensions: tuple[Dimension, ...]
    thresholds: tuple[Threshold, ...]
    sha256: str

    @property
    def max_total(self) -> int:
        return len(self.dimensions) * MAX_PER_DIMENSION

    def verdict(self, total: float) -> str:
        for t in self.thresholds:
            if t.low <= total <= t.high:
                return t.verdict
        return "UNKNOWN"

    def by_key(self, key: str) -> Dimension:
        for d in self.dimensions:
            if d.key == key:
                return d
        raise KeyError(f"no dimension {key!r}")


class RubricParseError(RuntimeError):
    pass


def load(path: str | Path) -> Rubric:
    path = Path(path)
    if not path.is_file():
        raise RubricParseError(f"no scoring rubric at {path}")
    text = path.read_text()

    dimensions = _parse_dimensions(text)
    if not dimensions:
        raise RubricParseError(f"{path} declares no '## Dimension N — name' sections")
    thresholds = _parse_thresholds(text)
    if not thresholds:
        raise RubricParseError(f"{path} declares no score-threshold table")

    return Rubric(
        dimensions=tuple(dimensions),
        thresholds=tuple(thresholds),
        sha256=hashlib.sha256(text.encode()).hexdigest(),
    )


def _parse_dimensions(text: str) -> list[Dimension]:
    dimensions: list[Dimension] = []
    number = name = question = None
    criteria: dict[int, str] = {}

    def flush():
        if number is not None and criteria:
            dimensions.append(Dimension(number, name, question or "", dict(criteria)))

    for line in text.splitlines():
        header = _DIMENSION.match(line)
        if header:
            flush()
            number, name = int(header.group(1)), header.group(2)
            question, criteria = None, {}
            continue
        if number is None:
            continue
        if _HEADING.match(line):
            flush()
            number = None
            continue
        row = _SCORE_ROW.match(line)
        if row:
            criteria[int(row.group(1))] = row.group(2)
        elif line.strip() and not _TABLE.match(line) and question is None:
            question = line.strip()

    flush()
    return dimensions


def _parse_thresholds(text: str) -> list[Threshold]:
    thresholds: list[Threshold] = []
    for line in text.splitlines():
        row = _THRESHOLD_ROW.match(line)
        if not row:
            continue
        low_hi, high, under, verdict, action = row.groups()
        if under is not None:
            thresholds.append(Threshold(0, int(under) - 1, verdict, action))
        else:
            thresholds.append(Threshold(int(low_hi), int(high), verdict, action))
    return thresholds
# <AI-Generated END>
