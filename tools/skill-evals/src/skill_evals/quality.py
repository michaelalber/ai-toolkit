# <AI-Generated START>
"""L3 — does invoking a skill actually produce good output?

The SKILL.md body becomes the system prompt; a realistic task becomes the user message;
the reply is judged against **that skill's own acceptance criteria**.

`derive_criteria` is what keeps this honest. Criteria are proposed mechanically from the
skill's own Non-Negotiable Constraints, workflow phase names, and state-block fields, then
edited by the author into the dataset. Without that, an output-quality eval degenerates
into asking a model "is this good?", which measures the judge's mood rather than the skill.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_CONSTRAINT = re.compile(r"^\s*\d+\.\s+(.+?)\s*$")
_CONSTRAINTS_HEADER = re.compile(r"non-negotiable constraints", re.IGNORECASE)
_PHASE = re.compile(r"^([A-Z][A-Z0-9 -]+)(?:\s{2,}|$)")
_STATE_FIELD = re.compile(r"^([a-z][a-z0-9_]*)\s*:")
_EXIT = re.compile(r"\*\*Exit criteria:\*\*\s*(.+)", re.IGNORECASE)


@dataclass(frozen=True)
class DerivedCriteria:
    constraints: list[str]
    phases: list[str]
    state_fields: list[str]
    exit_criteria: str | None

    def as_list(self) -> list[str]:
        """Criteria phrased as things a judge can check in a transcript."""
        out: list[str] = []
        if self.state_fields:
            shown = ", ".join(self.state_fields[:5])
            out.append(f"Emits a state block carrying: {shown}")
        if self.phases:
            out.append("Proceeds through the workflow phases in order: "
                       + " -> ".join(self.phases))
        out += [f"Honours the constraint: {c}" for c in self.constraints]
        if self.exit_criteria:
            out.append(f"Meets the stated exit criteria: {self.exit_criteria}")
        return out


def system_prompt(skill) -> str:
    """The SKILL.md body with frontmatter stripped — what the harness actually injects."""
    return skill.body.strip()


def derive_criteria(skill) -> DerivedCriteria:
    return DerivedCriteria(
        constraints=_constraints(skill),
        phases=_phases(skill),
        state_fields=_state_fields(skill),
        exit_criteria=_exit_criteria(skill),
    )


def _constraints(skill) -> list[str]:
    lines = skill.section_lines("Core Philosophy")
    found: list[str] = []
    started = False
    for line in lines:
        if _CONSTRAINTS_HEADER.search(line):
            started = True
            continue
        if not started:
            continue
        match = _CONSTRAINT.match(line)
        if match:
            found.append(_first_clause(match.group(1)))
        elif found and line.strip() and not line.startswith((" ", "\t")):
            break
    return found


def _phases(skill) -> list[str]:
    """Phase names from the fenced Workflow block — e.g. DETECT, SCAFFOLD, VERIFY."""
    phases: list[str] = []
    for line in skill.section_lines("Workflow"):
        match = _PHASE.match(line)
        if match:
            name = match.group(1).strip()
            # 2 chars is the floor, not 3: cargo-package-scaffold has a `CI` phase.
            if 1 < len(name) <= 24 and name not in phases:
                phases.append(name)
    return phases


def _state_fields(skill) -> list[str]:
    if not skill.state_tags:
        return []
    tag = skill.state_tags[0]
    block = re.search(rf"<{re.escape(tag)}>(.*?)</{re.escape(tag)}>", skill.text, re.DOTALL)
    if not block:
        return []
    fields: list[str] = []
    for line in block.group(1).splitlines():
        match = _STATE_FIELD.match(line.strip())
        if match and match.group(1) not in fields:
            fields.append(match.group(1))
    return fields


def _exit_criteria(skill) -> str | None:
    match = _EXIT.search(skill.text)
    return _first_clause(match.group(1)) if match else None


def _first_clause(text: str) -> str:
    """Trim a constraint to its actionable head — the rest is usually rationale."""
    text = re.sub(r"[`*]", "", text).strip()
    for separator in (" -- ", " — ", "; "):
        if separator in text:
            text = text.split(separator)[0]
    return text.rstrip(".").strip()
# <AI-Generated END>
