# <AI-Generated START>
"""Skill tier classification.

Which rules apply to a skill depends on what kind of skill it is, so this runs before any
structural rule. The tiers come from the repo's own two-tier system (CLAUDE.md § Skill
Tiers) plus the 2026-07-22 decision that a sub-20-line skill needs no ``references/`` at
all — a skill that fits in 19 lines has no depth to relocate, and a filler reference file
satisfies the letter of the rule while defeating its purpose.
"""

from __future__ import annotations

from enum import Enum

CANONICAL_SECTIONS = (
    "Core Philosophy",
    "Workflow",
    "State Block",
    "Output Template",
    "Integration",
)

EXEMPT_MAX_LINES = 19
MINIMAL_MAX_LINES = 100
FULL_MAX_LINES = 200

_FULL_SECTION_THRESHOLD = 3


class Tier(Enum):
    EXEMPT = "exempt"
    """Under 20 lines. No section structure, no references required."""

    MINIMAL = "minimal"
    """Mode switches, conversational tools, thin workflow-phase drivers."""

    FULL = "full"
    """Domain-expert skills on the 5-section lean layout."""


def classify(skill) -> Tier:
    """Tier is decided by size, not by section count.

    Section count is tempting but wrong: the QRSPI/QRASPI phase drivers are declared
    minimal-tier by the 2026-06-02 decision yet adopt the full 5-section shape for
    consistency. Promoting them on that basis would demand depth they deliberately do not
    have. Size is what signals "there is depth here to relocate" — which is the entire
    reason the reference-file requirement exists.
    """
    if skill.line_count <= EXEMPT_MAX_LINES:
        return Tier.EXEMPT
    if skill.line_count > MINIMAL_MAX_LINES:
        return Tier.FULL
    return Tier.MINIMAL


def max_lines(tier: Tier) -> int | None:
    return {Tier.EXEMPT: None, Tier.MINIMAL: MINIMAL_MAX_LINES, Tier.FULL: FULL_MAX_LINES}[tier]


def min_reference_files(tier: Tier) -> int:
    return {Tier.EXEMPT: 0, Tier.MINIMAL: 1, Tier.FULL: 2}[tier]


def _canonical_section_count(skill) -> int:
    return sum(1 for prefix in CANONICAL_SECTIONS if skill.has_section(prefix))
# <AI-Generated END>
