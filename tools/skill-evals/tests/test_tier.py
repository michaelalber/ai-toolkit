from pathlib import Path

from conftest import write_good_full, write_good_minimal, write_skill, write_tiny

from skill_evals.corpus import load_skill
from skill_evals.tier import Tier, classify


def _tier(skills_dir: Path, name: str) -> Tier:
    return classify(load_skill(skills_dir / name))


def test_under_20_lines_is_exempt(skills_dir: Path):
    write_tiny(skills_dir)
    assert _tier(skills_dir, "tiny-shim") is Tier.EXEMPT


def test_exempt_boundary_is_strictly_under_20(skills_dir: Path):
    write_skill(skills_dir, "at-19", raw="\n".join(["x"] * 19))
    write_skill(skills_dir, "at-20", raw="\n".join(["x"] * 20))
    assert _tier(skills_dir, "at-19") is Tier.EXEMPT
    assert _tier(skills_dir, "at-20") is not Tier.EXEMPT


def test_canonical_layout_is_full(skills_dir: Path):
    write_good_full(skills_dir)
    assert _tier(skills_dir, "good-full") is Tier.FULL


def test_short_focused_instructions_are_minimal(skills_dir: Path):
    write_good_minimal(skills_dir)
    assert _tier(skills_dir, "good-minimal") is Tier.MINIMAL


def _pad(body: str, to: int = 40) -> str:
    """Lift a body clear of the sub-20-line EXEMPT tier without adding structure."""
    return body + "\n" + "\n".join(f"prose line {i}" for i in range(to))


def test_a_short_phase_driver_with_all_five_sections_is_minimal(skills_dir: Path):
    """The QRSPI/QRASPI phase skills: 86-110 lines, 5 sections, one reference file.

    The 2026-06-02 decision declares them minimal-tier — "thin, self-sufficient
    workflow-phase drivers". They adopt the 5-section shape for consistency, and
    promoting them to FULL on section count alone would demand depth they do not have.
    Size is the signal for "there is depth here"; section count is not.
    """
    body = _pad(
        "# T\n\n## Core Philosophy\n\nx\n\n## Workflow\n\ny\n\n## State Block\n\nz\n\n"
        "## Output Template\n\no\n\n## Integration with Other Skills\n\ni\n",
        to=40,
    )
    write_skill(skills_dir, "qrspi-phase", body=body, references={"a.md": "x"})
    assert _tier(skills_dir, "qrspi-phase") is Tier.MINIMAL


def test_the_minimal_ceiling_is_what_promotes_a_skill_to_full(skills_dir: Path):
    write_skill(skills_dir, "at-100", raw="\n".join(["x"] * 100))
    write_skill(skills_dir, "at-101", raw="\n".join(["x"] * 101))
    assert load_skill(skills_dir / "at-100").line_count == 100
    assert _tier(skills_dir, "at-100") is Tier.MINIMAL
    assert _tier(skills_dir, "at-101") is Tier.FULL


def test_over_100_lines_is_full_regardless_of_sections(skills_dir: Path):
    """There is no oversized minimal tier — past the minimal budget you are FULL."""
    body = "# T\n\n" + "\n".join(f"prose line {i}" for i in range(120))
    write_skill(skills_dir, "long", body=body, references={"a.md": "x"})
    assert _tier(skills_dir, "long") is Tier.FULL


# <AI-Generated START>
# --- attempts_five_section_layout: synthetic cover for the three cases the real-corpus
# test used to pin (its conversational examples — grilling, domain-model — were deleted).


def _attempts(skills_dir: Path, name: str) -> bool:
    from skill_evals.tier import attempts_five_section_layout

    return attempts_five_section_layout(load_skill(skills_dir / name))


def test_a_conversational_minimal_skill_never_attempts_the_layout(skills_dir: Path):
    body = _pad("# Grill\n\nInterview the user one question at a time.\n", to=40)
    write_skill(skills_dir, "conversational", body=body, references={"a.md": "x"})
    assert not _attempts(skills_dir, "conversational")


def test_an_incidental_integration_heading_alone_is_not_an_attempt(skills_dir: Path):
    body = _pad("# Vocab\n\nGlossary.\n\n## Integration with Other Skills\n\ni\n", to=40)
    write_skill(skills_dir, "vocab", body=body, references={"a.md": "x"})
    assert not _attempts(skills_dir, "vocab")


def test_a_short_skill_with_a_distinctive_heading_is_attempting(skills_dir: Path):
    body = _pad("# T\n\n## Core Philosophy\n\nx\n", to=40)
    write_skill(skills_dir, "short-lean", body=body, references={"a.md": "x"})
    assert _attempts(skills_dir, "short-lean")


def test_a_full_tier_skill_with_no_canonical_sections_still_counts_as_attempting(
    skills_dir: Path,
):
    """Full tier is always judged: missing sections there are tracked debt, not exemption."""
    body = "# T\n\n## Two Modes\n\n" + "\n".join(f"prose line {i}" for i in range(120))
    write_skill(skills_dir, "bespoke-full", body=body, references={"a.md": "x", "b.md": "y"})
    assert _attempts(skills_dir, "bespoke-full")
# <AI-Generated END>
