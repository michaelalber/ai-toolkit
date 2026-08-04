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


def canonical_section_count(skill) -> int:
    """How many of the 5 canonical section headings this skill actually has.

    Independent of tier: a minimal-tier skill can adopt all 5 (QRSPI/QRASPI phase
    drivers, ``cargo-package-scaffold``) while a genuinely conversational skill
    (``grilling``, ``domain-model``) adopts none. A purely informational count — the
    scorecard's applicability decision uses ``attempts_five_section_layout`` below,
    not this count directly.
    """
    return sum(1 for prefix in CANONICAL_SECTIONS if skill.has_section(prefix))


# "Integration" is deliberately excluded from the layout-attempt signal: it is the
# least distinctive of the 5 headings — a near-universal "what this pairs with" note
# that a skill can carry (``codebase-design``: ``## Integration with Other Skills``)
# without that implying it adopted Core Philosophy/Workflow/State Block/Output
# Template. Including it produced a false negative: codebase-design's one incidental
# match masked that it never attempted the layout.
_LAYOUT_SIGNAL_SECTIONS = ("Core Philosophy", "Workflow", "State Block", "Output Template")


def attempts_five_section_layout(skill) -> bool:
    """Was this skill even trying to follow the 5-section lean layout?

    Full tier is always "trying" — a full-template skill with zero matching sections
    (``substack-writer``) hasn't adopted the layout yet, which is real, tracked debt
    (SK021 in ``baselines/known-defects.yaml``), not evidence it was never attempting
    one. Below full tier, "trying" is decided by evidence: a minimal/exempt skill with
    at least one of the four distinctive headings (the QRSPI/QRASPI phase drivers,
    ``cargo-package-scaffold``) is judged on the full rubric like any full-template
    skill; one with none of them (``grilling``, ``domain-model``,
    ``improve-codebase-architecture``, ``codebase-design``) was never attempting it by
    design, and grading it against that yardstick is a category error, not a finding.
    """
    if classify(skill) is Tier.FULL:
        return True
    return any(skill.has_section(prefix) for prefix in _LAYOUT_SIGNAL_SECTIONS)
# <AI-Generated END>
