# <AI-Generated START>
"""SK040-SK044 — the references/ contract.

SK042 is the rule that matters most: a SKILL.md naming a ``references/`` file that is not
there sends the model to fetch nothing. It is silent — the skill still "loads" — so it
survives review indefinitely. The ``tdd`` -> ``tdd-loop`` rename left exactly this defect.
"""

from __future__ import annotations

from ..findings import Finding, Severity
from ..tier import Tier, classify, min_reference_files
from . import rule

STUB_MAX_LINES = 20


def _f(rule_id, severity, skill, message, *, line=None, evals_tc=None) -> Finding:
    return Finding(rule_id, severity, message, skill.name, skill.skill_md, line, evals_tc)


@rule("SK040", severity=Severity.ERROR, summary="references/ exists", evals_tc="CI Gate")
def sk040_references_dir_exists(skill, ctx):
    tier = classify(skill)
    if tier is Tier.EXEMPT:
        return  # under 20 lines there is no depth to relocate
    if not (skill.path / "references").is_dir():
        yield _f("SK040", Severity.ERROR, skill,
                 f"{tier.value}-tier skill has no references/ directory", evals_tc="CI Gate")


@rule("SK041", severity=Severity.ERROR, summary="enough reference files for the tier",
      evals_tc="constraints.md")
def sk041_reference_count(skill, ctx):
    tier = classify(skill)
    required = min_reference_files(tier)
    if required == 0 or not (skill.path / "references").is_dir():
        return  # SK040 already reports a missing directory
    actual = len(skill.reference_files)
    if actual < required:
        yield _f("SK041", Severity.ERROR, skill,
                 f"{actual} reference file(s); {tier.value} tier requires {required}",
                 evals_tc="constraints.md")


@rule("SK042", severity=Severity.ERROR, summary="every references/ pointer resolves",
      evals_tc="TC1")
def sk042_pointers_resolve(skill, ctx):
    """Resolved relative to *this* skill's directory — where the model would look."""
    for pointer in skill.reference_pointers:
        if not (skill.path / pointer.target).exists():
            yield _f("SK042", Severity.ERROR, skill,
                     f"{pointer.target} does not exist under skills/{skill.name}/",
                     line=pointer.line, evals_tc="TC1")


@rule("SK043", severity=Severity.WARNING, summary="every reference file is pointed at",
      evals_tc="Rubric D9")
def sk043_references_are_reachable(skill, ctx):
    tier = classify(skill)
    if tier is Tier.EXEMPT:
        return
    named = {p.target for p in skill.reference_pointers}
    for path in skill.reference_files:
        relative = path.relative_to(skill.path).as_posix()
        if relative not in named:
            yield _f("SK043", Severity.WARNING, skill,
                     f"{relative} is never named in SKILL.md — it will not be discovered",
                     evals_tc="Rubric D9")


@rule("SK044", severity=Severity.WARNING, summary="reference files are not stubs",
      evals_tc="Rubric D8")
def sk044_references_have_substance(skill, ctx):
    for path in skill.reference_files:
        if path.suffix != ".md":
            continue
        n = len(path.read_text().splitlines())
        if n < STUB_MAX_LINES:
            yield _f("SK044", Severity.WARNING, skill,
                     f"{path.relative_to(skill.path).as_posix()} is {n} lines — a stub, not depth",
                     evals_tc="Rubric D8")
# <AI-Generated END>
