"""Acceptance and regression tests against the real skills/ tree.

Two jobs:

1. **Regression** — the defects the linter found on 2026-08-02 are fixed and must stay
   fixed. Each test names the rule and the skill, so a reintroduction says exactly what
   broke rather than "the lint failed".
2. **Green invariants** — the properties that already held (agent parity, the context
   mirror pair, frontmatter parsing) are asserted so they cannot quietly stop holding.

Proof that each *rule* fires lives in the synthetic-fixture suites; these tests prove the
rules were pointed at a real corpus and that the corpus is now clean.

Marked `corpus` and skipped when the tree is absent, so the unit suite stays hermetic.
Run with: pytest -m corpus
"""

from __future__ import annotations

from pathlib import Path

import pytest

from skill_evals.baselines import load_known_non_skills, load_state_tag_families
from skill_evals.corpus import discover, load_skill
from skill_evals.lint import lint

REPO_ROOT = Path(__file__).resolve().parents[3]
SKILLS = REPO_ROOT / "skills"
BASELINE = Path(__file__).resolve().parents[1] / "baselines" / "known-defects.yaml"

pytestmark = [
    pytest.mark.corpus,
    pytest.mark.skipif(not SKILLS.is_dir(), reason="real skills/ tree not present"),
]


def _lint(**kw):
    return lint(
        SKILLS,
        repo_root=REPO_ROOT,
        state_tag_families=load_state_tag_families(REPO_ROOT),
        known_non_skills=load_known_non_skills(REPO_ROOT),
        **kw,
    )


@pytest.fixture(scope="module")
def findings():
    return _lint()


@pytest.fixture(scope="module")
def gated():
    """What the documented gate command sees — the baseline applied."""
    return _lint(baseline=BASELINE)


def _skills_for(findings, rule_id) -> set[str]:
    return {f.skill for f in findings.for_rule(rule_id)}


def test_corpus_is_discovered():
    assert len(discover(SKILLS)) >= 90


def test_the_documented_gate_passes(gated):
    """`skill-evals lint --baseline baselines/known-defects.yaml` must exit 0."""
    assert gated.errors == [], [f"{f.rule_id} {f.skill}: {f.message}" for f in gated.errors]


def test_the_ungated_lint_still_reports_the_open_backlog(findings):
    """Baselined items are deferred, not resolved — a plain lint still names them.

    SK041 (qraspi-graduate, qraspi-implement, qraspi-plan, qrspi-research) was resolved by
    trimming each back under the minimal-tier line ceiling, not baselined — see the
    2026-08-02 known-defects.yaml entry this superseded.
    """
    assert {f.rule_id for f in findings.errors} == {"SK021", "SK030"}


def test_no_rule_crashed_on_the_real_corpus(findings):
    assert not [f for f in findings if "rule crashed" in f.message]


# --- regression: the tdd -> tdd-loop rename tail (2026-07-30) ----------------------


def test_tdd_agent_reference_pointers_resolve(findings):
    """Was: SKILL.md:103 named two references/ files that live under tdd-loop/."""
    assert "tdd-agent" not in _skills_for(findings, "SK042")


def test_no_integration_table_still_names_tdd(findings):
    """Was: 18 Integration rows naming `tdd` (and one naming `tdd-cycle`)."""
    assert findings.for_rule("SK050") == []


def test_tdd_loop_is_triaged_and_the_stale_row_is_gone(findings):
    assert findings.for_rule("SK053") == []
    assert findings.for_rule("SK054") == []


def test_readme_lists_tdd_loop_not_tdd(findings):
    assert findings.for_rule("SK056") == []


def test_the_dangling_targets_live_under_tdd_loop():
    """The defect was a stale *name*, not deleted content — content is still there."""
    for name in ("code-smells.md", "refactoring-catalog.md"):
        assert (SKILLS / "tdd-loop" / "references" / name).is_file()


# --- regression: metadata drift ----------------------------------------------------


def test_pi_triage_counts_agree_with_its_own_rows(findings):
    """Was: headings 38/52/6, rows 35/53/6, footer 34/45/6 = 85. Three sets, all different."""
    assert findings.for_rule("SK055") == []


def test_published_skill_counts_match_the_tree(findings):
    """Was: README at-a-glance 93, CLAUDE.md and AGENTS.md 87, against 94 real skills."""
    assert findings.for_rule("SK057") == []


def test_agent_parity_holds(findings):
    assert findings.for_rule("SK058") == []


def test_the_context_mirror_pair_is_byte_identical(findings):
    assert findings.for_rule("SK059") == []


# --- regression: state-tag ownership -----------------------------------------------


def test_no_state_tag_is_shared_outside_a_declared_family(findings):
    """Was: <tdd-state> on both tdd-loop and tdd-agent — a loop and its operating mode."""
    assert findings.for_rule("SK032") == []


def test_no_agent_reuses_a_skill_state_tag(findings):
    """Was: 4 agents (tdd, documentation, environment-health, research) on the skill's tag."""
    assert findings.for_rule("SK033") == []


def test_the_declared_families_are_the_two_parity_families():
    families = load_state_tag_families(REPO_ROOT)
    assert set(families) == {"arch-checklist-state", "security-review-state"}
    for tag, entry in families.items():
        assert entry.get("rationale"), f"{tag} is declared without a written rationale"


# --- the false-positive guard ------------------------------------------------------


@pytest.mark.parametrize("name", ["confluence-guide-writer", "jira-comment-writer"])
def test_sk005_does_not_fire_on_audience_inside_a_state_block(findings, name):
    """Both carry `audience: team` in frontmatter and a free-form `audience:` in state.

    A grep-based implementation reports these as malformed. This test fails if anyone
    ever rewrites SK005 as a grep.
    """
    assert name not in _skills_for(findings, "SK005")


@pytest.mark.parametrize("name", ["confluence-guide-writer", "jira-comment-writer"])
def test_those_skills_really_do_have_a_state_block_audience_line(name):
    skill = load_skill(SKILLS / name)
    assert skill.audience == "team"
    assert "audience:" in skill.text.split("---", 2)[2]  # after the frontmatter


def test_sk027_does_not_fire_on_id_format_placeholders(findings):
    """capture-consolidate teaches `REQ-XXX` / `DRAFT-NNN` ID formats, not TODOs."""
    assert "capture-consolidate" not in _skills_for(findings, "SK027")


def test_phase_drivers_are_not_promoted_to_full_on_section_count():
    """The QRSPI/QRASPI drivers under 100 lines are minimal-tier despite 5 sections."""
    from skill_evals.tier import Tier, classify

    for name in ("qrspi-questions", "qrspi-plan", "qrspi-implement", "qraspi-questions"):
        skill = load_skill(SKILLS / name)
        assert classify(skill) is Tier.MINIMAL, f"{name} is {skill.line_count} lines"


def test_conversational_skills_never_attempted_the_layout_but_others_do_or_should():
    """Pins the fact the L4 scorecard's section gate (``attempts_five_section_layout``)
    relies on — three ways a skill's relationship to the 5-section layout can go:

    1. Never attempting it, by design: ``grilling``/``grill-me``/``grill-with-docs``/
       ``domain-model``/``improve-codebase-architecture`` (minimal/exempt tier, zero of
       the four distinctive headings) and ``codebase-design`` (minimal tier, whose only
       match is the near-universal ``Integration`` heading, which doesn't count — see
       ``tier._LAYOUT_SIGNAL_SECTIONS``). The scorecard's 2026-08-02 full sweep
       DEPRECATE-verdicted these purely for lacking a layout they were never meant to
       have — that's the bug this gate fixes.
    2. Adopting it despite being short: ``cargo-package-scaffold`` is MINIMAL-tier by
       size (99 lines) yet has all 5 canonical sections — the documented full-template
       gold standard, just lean. Must stay judged on every dimension.
    3. Meant to have it but hasn't yet: ``substack-writer`` is FULL-tier with zero
       matching sections — a real, already-tracked lean-layout defect (SK021 in
       ``baselines/known-defects.yaml``), not evidence it was never attempting one.
       Gating this would silently convert a tracked finding into a non-finding, which
       the baseline's own rule forbids. Must also stay judged on every dimension.
    """
    from skill_evals.tier import attempts_five_section_layout

    never_attempting = (
        "grilling", "grill-me", "grill-with-docs", "domain-model",
        "improve-codebase-architecture", "codebase-design",
    )
    for name in never_attempting:
        skill = load_skill(SKILLS / name)
        assert not attempts_five_section_layout(skill), f"{name} unexpectedly attempts it"

    for name in ("cargo-package-scaffold", "substack-writer"):
        skill = load_skill(SKILLS / name)
        assert attempts_five_section_layout(skill), f"{name} must stay judged on all dimensions"


# --- the evals.md gate this tool replaces ------------------------------------------


def test_the_evals_md_pi_grep_matches_nothing():
    """The documented CI-gate grep assumes backticked rows. They are not backticked.

    This is why the gate always reported every skill as untriaged, and why SK053 parses
    the table instead of grepping it.
    """
    import re

    text = (REPO_ROOT / "pi" / "SKILLS-local.md").read_text()
    documented_grep = re.compile(r"^\| `([^`]+)", re.MULTILINE)
    assert documented_grep.findall(text) == []


# --- open: what the lean-layout migration did not cover ----------------------------


def test_lean_layout_migration_is_complete_on_line_count(findings):
    """This part of the 2026-06-26 decision does hold — every skill is within budget."""
    assert findings.for_rule("SK020") == []


def test_lean_layout_migration_is_incomplete_on_sections(findings):
    """This part does not.

    The decision records the migration as complete; it was verified on line count only.
    Over a hundred non-canonical `##` sections remain — AI Discipline Rules, Error
    Recovery, Anti-Patterns, Domain Principles — the exact four the 2026-06-03 decision
    said must move to references/. They are warnings, so they do not gate; this test
    keeps the claim and the reality linked until someone closes the gap.
    """
    leftovers = findings.for_rule("SK023")
    assert leftovers, "SK023 is clean — update the 2026-06-26 decision and delete this test"
