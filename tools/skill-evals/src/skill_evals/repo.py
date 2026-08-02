# <AI-Generated START>
"""Parsers for the repo-level documents that must stay in sync with ``skills/``.

Each parser is deliberately tolerant: a missing or restructured document yields empty
results so the matching rule stays silent, rather than the linter crashing on a repo whose
layout has moved on.

``pi/SKILLS-local.md`` rows are **not** backticked — the grep in ``evals.md``'s CI Gate
assumes they are, which is why it has always matched nothing and reported every skill as
untriaged.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

_PI_HEADER = re.compile(r"^##\s*(🟢|🟡|🔴)\s*(\w+).*?\((\d+)\)\s*$")
_PI_COUNTS = re.compile(r"Counts:\s*🟢\s*(\d+)\s*·\s*🟡\s*(\d+)\s*·\s*🔴\s*(\d+)\s*=\s*(\d+)")
_TABLE_ROW = re.compile(r"^\|\s*([^|]+?)\s*\|")
_TABLE_SEP = re.compile(r"^\s*\|[\s:|-]+\|")
_SKILL_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

_BADGE_SKILLS = re.compile(r"badge/skills-(\d+)-")
_BADGE_AGENTS = re.compile(r"badge/agents-(\d+)-")
_PROSE_COUNTS = re.compile(r"\*\*(\d+)\s+skills,\s*(\d+)\s+agents,\s*and\s+(\d+)\s+slash commands")
_GLANCE_ROW = re.compile(r"^\|\s*(?:\*\*)?([^|*]+?)(?:\*\*)?\s*\|\s*(\d+)\s*\|")


@dataclass
class PiTriage:
    """The Green/Yellow/Red routing table for local-model use."""

    tiers: dict[str, list[str]] = field(default_factory=dict)
    declared_header_counts: dict[str, int] = field(default_factory=dict)
    declared_footer_counts: tuple[int, int, int, int] | None = None
    present: bool = False

    @property
    def all_names(self) -> list[str]:
        return [name for names in self.tiers.values() for name in names]

    def row_counts(self) -> dict[str, int]:
        return {tier: len(names) for tier, names in self.tiers.items()}


def parse_pi_triage(path: Path) -> PiTriage:
    if not path.is_file():
        return PiTriage()
    triage = PiTriage(present=True)
    current: str | None = None
    for line in path.read_text().splitlines():
        header = _PI_HEADER.match(line)
        if header:
            current = header.group(1)
            triage.tiers.setdefault(current, [])
            triage.declared_header_counts[current] = int(header.group(3))
            continue
        counts = _PI_COUNTS.search(line)
        if counts:
            triage.declared_footer_counts = tuple(int(g) for g in counts.groups())  # type: ignore
            continue
        if current and (name := _first_cell(line)):
            triage.tiers[current].append(name)
    return triage


@dataclass
class ReadmeIndex:
    """Skill names listed in the README's suite tables, and its count claims."""

    listed: dict[str, list[str]] = field(default_factory=dict)
    badge_skills: int | None = None
    badge_agents: int | None = None
    prose_skills: int | None = None
    prose_agents: int | None = None
    prose_commands: int | None = None
    glance: dict[str, int] = field(default_factory=dict)
    present: bool = False

    @property
    def all_names(self) -> list[str]:
        return [name for names in self.listed.values() for name in names]

    @property
    def glance_skill_total(self) -> int | None:
        team = self.glance.get("Skills (team)")
        professional = self.glance.get("Skills (professional)")
        if team is None or professional is None:
            return None
        return team + professional


def parse_readme(path: Path) -> ReadmeIndex:
    if not path.is_file():
        return ReadmeIndex()
    index = ReadmeIndex(present=True)
    section = "<none>"
    in_skills = False
    for line in path.read_text().splitlines():
        if line.startswith("## "):
            # Only the top-level Skills sections list skills; the Agents and Commands
            # sections use the same backticked-first-column table shape.
            in_skills = "skills" in line.lower()
            section = line.lstrip("# ").strip()
        elif line.startswith("###"):
            section = line.lstrip("# ").strip()
        if (badge := _BADGE_SKILLS.search(line)) and index.badge_skills is None:
            index.badge_skills = int(badge.group(1))
        if (badge := _BADGE_AGENTS.search(line)) and index.badge_agents is None:
            index.badge_agents = int(badge.group(1))
        if (prose := _PROSE_COUNTS.search(line)) and index.prose_skills is None:
            index.prose_skills, index.prose_agents, index.prose_commands = (
                int(prose.group(1)), int(prose.group(2)), int(prose.group(3))
            )
        if (row := _GLANCE_ROW.match(line)) and not row.group(1).startswith("`"):
            index.glance.setdefault(row.group(1).strip(), int(row.group(2)))
        if in_skills and (name := _backticked_first_cell(line)):
            index.listed.setdefault(section, []).append(name)
    return index


def count_claims(path: Path) -> list[tuple[int, int]]:
    """``(line number, claimed skill count)`` for 'N skills' claims in a context file."""
    if not path.is_file():
        return []
    claims = []
    for lineno, line in enumerate(path.read_text().splitlines(), start=1):
        for match in re.finditer(r"(?<![\d.])(\d{2,3})\s+(?:shareable\s+)?skills\b", line):
            claims.append((lineno, int(match.group(1))))
    return claims


def agent_names(root: Path, platform: str) -> set[str]:
    base = root / platform / "agents"
    if not base.is_dir():
        return set()
    return {p.stem for p in base.rglob("*.md")}


def _first_cell(line: str) -> str | None:
    if _TABLE_SEP.match(line):
        return None
    match = _TABLE_ROW.match(line)
    if not match:
        return None
    cell = match.group(1).strip().strip("`").strip()
    return cell if _SKILL_NAME.match(cell) else None


def _backticked_first_cell(line: str) -> str | None:
    if _TABLE_SEP.match(line):
        return None
    match = re.match(r"^\|\s*`([^`]+)`\s*\|", line)
    if not match:
        return None
    cell = match.group(1).strip()
    return cell if _SKILL_NAME.match(cell) else None
# <AI-Generated END>
