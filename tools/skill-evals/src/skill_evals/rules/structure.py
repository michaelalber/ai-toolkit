# <AI-Generated START>
"""SK020-SK027 — the 5-section lean layout and its line budget.

Every always-loaded section is a per-invocation token tax, worst on smaller local models.
These rules enforce that depth lives in ``references/`` and loads just-in-time, which is
the whole point of the lean layout.
"""

from __future__ import annotations

import re

from ..findings import Finding, Severity
from ..tier import CANONICAL_SECTIONS, Tier, classify, max_lines
from . import rule

# 3-6 rather than the rubric's 3-5: qraspi-skeleton, a stated gold standard, carries 6.
# A rule that fails the exemplar is measuring the wrong thing.
MIN_CONSTRAINTS = 3
MAX_CONSTRAINTS = 6

MAX_TABLE_ROWS = 6

# Not adjacent to a word char or hyphen: `REQ-XXX` and `DRAFT-NNN` are ID *formats* that
# capture-consolidate teaches, not unfinished text. A plain \b would match inside them.
_ISOLATED = r"(?<![\w-]){}(?![\w-])"

PLACEHOLDER_PATTERNS = (
    re.compile(_ISOLATED.format("TODO")),
    re.compile(_ISOLATED.format("FIXME")),
    re.compile(_ISOLATED.format("XXX")),
    re.compile(r"\[fill in[^\]]*\]", re.IGNORECASE),
    re.compile(r"\bLorem ipsum\b", re.IGNORECASE),
)

_FENCE = re.compile(r"^\s*(```|~~~)")
_NUMBERED = re.compile(r"^\s*(\d+)\.\s+\S")
_TABLE_ROW = re.compile(r"^\s*\|.*\|\s*$")
_TABLE_SEP = re.compile(r"^\s*\|[\s:|-]+\|\s*$")
_CONSTRAINTS_HEADER = re.compile(r"non-negotiable constraints", re.IGNORECASE)


def _f(rule_id, severity, skill, message, *, line=None, evals_tc=None) -> Finding:
    return Finding(rule_id, severity, message, skill.name, skill.skill_md, line, evals_tc)


@rule("SK020", severity=Severity.ERROR, summary="within the tier's line budget",
      evals_tc="TC1, Taste Rule 1")
def sk020_line_budget(skill, ctx):
    limit = max_lines(classify(skill))
    if limit is not None and skill.line_count > limit:
        yield _f("SK020", Severity.ERROR, skill,
                 f"{skill.line_count} lines exceeds the {classify(skill).value} budget of {limit}"
                 " — move depth into references/",
                 evals_tc="TC1")


@rule("SK021", severity=Severity.ERROR, summary="all 5 canonical sections present",
      evals_tc="TC1")
def sk021_sections_present(skill, ctx):
    if classify(skill) is not Tier.FULL:
        return
    missing = [name for name in CANONICAL_SECTIONS if not skill.has_section(name)]
    if missing:
        yield _f("SK021", Severity.ERROR, skill,
                 f"missing canonical section(s): {', '.join(missing)}", evals_tc="TC1")


@rule("SK022", severity=Severity.WARNING, summary="canonical sections in order", evals_tc="TC1")
def sk022_section_order(skill, ctx):
    if classify(skill) is not Tier.FULL:
        return
    present = [
        name
        for name in skill.sections
        if any(name.startswith(canon) for canon in CANONICAL_SECTIONS)
    ]
    canonical_index = {}
    for name in present:
        for idx, canon in enumerate(CANONICAL_SECTIONS):
            if name.startswith(canon):
                canonical_index[name] = idx
                break
    order = [canonical_index[name] for name in present]
    if order != sorted(order):
        yield _f("SK022", Severity.WARNING, skill,
                 f"canonical sections out of order: {' -> '.join(present)}", evals_tc="TC1")


@rule("SK023", severity=Severity.WARNING, summary="no sections outside the canonical set",
      evals_tc="Taste Rule 1")
def sk023_no_extra_sections(skill, ctx):
    """Depth sections (Anti-Patterns, Error Recovery, AI Discipline) belong in references/."""
    if classify(skill) is not Tier.FULL:
        return
    for name in skill.sections:
        if not any(name.startswith(canon) for canon in CANONICAL_SECTIONS):
            yield _f("SK023", Severity.WARNING, skill,
                     f"non-canonical section '## {name}' — relocate this depth to references/",
                     evals_tc="Taste Rule 1")


@rule("SK024", severity=Severity.WARNING, summary="title is followed by an epigraph",
      evals_tc="Lean Layout")
def sk024_epigraph(skill, ctx):
    if classify(skill) is not Tier.FULL:
        return
    lines = skill.lines
    for idx, line in enumerate(lines):
        if line.startswith("# "):
            window = lines[idx + 1 : idx + 6]
            if not any(w.lstrip().startswith(">") for w in window):
                yield _f("SK024", Severity.WARNING, skill,
                         "no '> ' epigraph within 5 lines of the title", line=idx + 1,
                         evals_tc="Lean Layout")
            return


@rule("SK025", severity=Severity.WARNING, summary="3-6 numbered Non-Negotiable Constraints",
      evals_tc="TC1")
def sk025_constraints_count(skill, ctx):
    if classify(skill) is not Tier.FULL:
        return
    numbers = _constraint_numbers(skill)
    if not numbers:
        yield _f("SK025", Severity.WARNING, skill,
                 "Core Philosophy has no numbered 'Non-Negotiable Constraints' list",
                 evals_tc="TC1")
    elif not MIN_CONSTRAINTS <= len(numbers) <= MAX_CONSTRAINTS:
        yield _f("SK025", Severity.WARNING, skill,
                 f"{len(numbers)} Non-Negotiable Constraints; expected "
                 f"{MIN_CONSTRAINTS}-{MAX_CONSTRAINTS}", evals_tc="TC1")


@rule("SK025b", severity=Severity.WARNING, summary="constraints numbered sequentially",
      evals_tc="TC1")
def sk025b_constraints_sequential(skill, ctx):
    if classify(skill) is not Tier.FULL:
        return
    numbers = _constraint_numbers(skill)
    if numbers and numbers != list(range(1, len(numbers) + 1)):
        yield _f("SK025b", Severity.WARNING, skill,
                 f"Non-Negotiable Constraints are numbered {numbers}, not sequential",
                 evals_tc="TC1")


@rule("SK026", severity=Severity.WARNING, summary="no large tables outside Integration",
      evals_tc="Taste Rule 1")
def sk026_no_large_tables(skill, ctx):
    """A long principle or anti-pattern table inline is the lean layout's main regression."""
    if classify(skill) is not Tier.FULL:
        return
    integration = set(skill.section_lines("Integration"))
    for start_line, size in _tables(skill.lines):
        rows = skill.lines[start_line - 1 : start_line - 1 + size]
        if rows and rows[0] in integration:
            continue
        body_rows = size - 2  # header + separator
        if body_rows > MAX_TABLE_ROWS:
            yield _f("SK026", Severity.WARNING, skill,
                     f"{body_rows}-row table inline — depth tables belong in references/",
                     line=start_line, evals_tc="Taste Rule 1")


@rule("SK027", severity=Severity.ERROR, summary="no placeholder text", evals_tc="CI Gate")
def sk027_no_placeholders(skill, ctx):
    for lineno, line in _outside_fences(skill.lines):
        for pattern in PLACEHOLDER_PATTERNS:
            if pattern.search(line):
                yield _f("SK027", Severity.ERROR, skill,
                         f"placeholder text: {line.strip()[:70]!r}", line=lineno,
                         evals_tc="CI Gate")
                break


def _constraint_numbers(skill) -> list[int]:
    """The list numbers under the 'Non-Negotiable Constraints' heading in Core Philosophy."""
    lines = skill.section_lines("Core Philosophy")
    numbers: list[int] = []
    started = False
    for line in lines:
        if _CONSTRAINTS_HEADER.search(line):
            started = True
            continue
        if not started:
            continue
        match = _NUMBERED.match(line)
        if match:
            numbers.append(int(match.group(1)))
        elif numbers and line.strip() and not line.startswith(("   ", "\t")):
            break  # the list ended
    return numbers


def _tables(lines: list[str]) -> list[tuple[int, int]]:
    """``(1-indexed start line, row count)`` for each markdown table."""
    found: list[tuple[int, int]] = []
    start = None
    count = 0
    in_fence = False
    for lineno, line in enumerate(lines, start=1):
        if _FENCE.match(line):
            in_fence = not in_fence
        if in_fence:
            continue
        if _TABLE_ROW.match(line):
            if start is None:
                start, count = lineno, 0
            count += 1
        elif start is not None:
            found.append((start, count))
            start, count = None, 0
    if start is not None:
        found.append((start, count))
    return [(s, c) for s, c in found if c >= 2 and _has_separator(lines, s, c)]


def _has_separator(lines: list[str], start: int, count: int) -> bool:
    return any(_TABLE_SEP.match(line) for line in lines[start - 1 : start - 1 + count])


def _outside_fences(lines: list[str]):
    in_fence = False
    for lineno, line in enumerate(lines, start=1):
        if _FENCE.match(line):
            in_fence = not in_fence
            continue
        if not in_fence:
            yield lineno, line
# <AI-Generated END>
