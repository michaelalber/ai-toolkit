# <AI-Generated START>
"""SK001-SK010 — frontmatter schema and description quality.

The description field is the only thing the model sees when deciding which skill to load,
so its quality *is* trigger reliability. Structure rules are errors; phrasing rules are
warnings, because 40 of the 94 skills currently carry no negative-boundary clause and a
lint that fails on 43% of the corpus on day one gets switched off rather than fixed.
"""

from __future__ import annotations

from ..findings import Finding, Severity
from . import rule

VALID_AUDIENCES = {"team", "professional"}

KNOWN_KEYS = {
    "name",
    "description",
    "audience",
    "source",
    "source_commit",
    "source_note",
    "disable-model-invocation",
    "references",
}

MAX_DESCRIPTION_CHARS = 1024

TRIGGER_MARKERS = ("use when", "use for", "use this skill when", "triggers on", "trigger for")
NEGATIVE_MARKERS = ("do not use", "don't use", "not for", "not when", "does not", "do NOT use")
FIRST_PERSON_STARTS = ("i ", "i'll", "we ", "we'll", "you ", "you'll", "you can", "let me")


def _f(rule_id, severity, skill, message, *, line=None, evals_tc=None) -> Finding:
    return Finding(
        rule_id=rule_id,
        severity=severity,
        message=message,
        skill=skill.name,
        file=skill.skill_md,
        line=line,
        evals_tc=evals_tc,
    )


@rule("SK001", severity=Severity.ERROR, summary="frontmatter parses as a YAML mapping",
      evals_tc="CI Gate")
def sk001_frontmatter_parses(skill, ctx):
    if skill.frontmatter is None:
        yield _f("SK001", Severity.ERROR, skill,
                 "no parseable YAML frontmatter block (missing, unterminated, or not a mapping)",
                 line=1, evals_tc="CI Gate")


@rule("SK002", severity=Severity.ERROR, summary="name matches the directory", evals_tc="TC1, TC7")
def sk002_name_matches_directory(skill, ctx):
    if skill.frontmatter is None:
        return
    declared = skill.declared_name
    if not declared:
        yield _f("SK002", Severity.ERROR, skill, "frontmatter has no 'name'", evals_tc="TC1")
    elif declared != skill.name:
        # The directory name is the identity Claude Code resolves; a mismatch means every
        # skill({name: ...}) call and Integration cross-reference points at nothing.
        yield _f("SK002", Severity.ERROR, skill,
                 f"name: {declared!r} does not match the directory {skill.name!r}",
                 evals_tc="TC1, TC7")


@rule("SK003", severity=Severity.ERROR, summary="description present", evals_tc="CI Gate")
def sk003_description_present(skill, ctx):
    if skill.frontmatter is None:
        return
    if not skill.description:
        yield _f("SK003", Severity.ERROR, skill, "frontmatter has no 'description'",
                 evals_tc="CI Gate")


@rule("SK004", severity=Severity.ERROR, summary="description within 1024 chars",
      evals_tc="Description Format")
def sk004_description_length(skill, ctx):
    n = len(skill.description)
    if n > MAX_DESCRIPTION_CHARS:
        yield _f("SK004", Severity.ERROR, skill,
                 f"description is {n} chars, over the {MAX_DESCRIPTION_CHARS} limit",
                 evals_tc="Description Format")


@rule("SK005", severity=Severity.ERROR, summary="audience is team or professional",
      evals_tc="TC1")
def sk005_audience_valid(skill, ctx):
    """Parsed from the frontmatter mapping, never grepped.

    Several skills legitimately carry an ``audience:`` line inside their *state block*
    (jira-comment-writer's `client | pm_formal | pm_friendly`, for one). A grep-based
    implementation reports those as malformed frontmatter; they are not.
    """
    if skill.frontmatter is None:
        return
    audience = skill.audience
    if audience is None:
        yield _f("SK005", Severity.ERROR, skill, "frontmatter has no 'audience'", evals_tc="TC1")
    elif audience not in VALID_AUDIENCES:
        yield _f("SK005", Severity.ERROR, skill,
                 f"audience: {audience!r} is not one of {sorted(VALID_AUDIENCES)}", evals_tc="TC1")


@rule("SK006", severity=Severity.WARNING, summary="description is third person",
      evals_tc="Description Format")
def sk006_third_person(skill, ctx):
    lowered = skill.description.lstrip().lower()
    if any(lowered.startswith(start) for start in FIRST_PERSON_STARTS):
        yield _f("SK006", Severity.WARNING, skill,
                 "description opens in first/second person; use 'Scaffolds...', 'Audits...'",
                 evals_tc="Description Format")


@rule("SK007", severity=Severity.WARNING, summary="description states when to use",
      evals_tc="TC1")
def sk007_has_trigger_clause(skill, ctx):
    lowered = skill.description.lower()
    if skill.description and not any(marker in lowered for marker in TRIGGER_MARKERS):
        yield _f("SK007", Severity.WARNING, skill,
                 "description has no trigger clause ('Use when ...' / 'Triggers on ...')",
                 evals_tc="TC1")


@rule("SK008", severity=Severity.WARNING, summary="description states when NOT to use",
      evals_tc="TC1")
def sk008_has_negative_boundary(skill, ctx):
    """The main defence against a skill firing on an adjacent skill's territory."""
    lowered = skill.description.lower()
    if skill.description and not any(marker.lower() in lowered for marker in NEGATIVE_MARKERS):
        yield _f("SK008", Severity.WARNING, skill,
                 "description has no negative boundary ('Do NOT use when ...' / 'Not for ...')",
                 evals_tc="TC1")


@rule("SK009", severity=Severity.WARNING, summary="no unknown frontmatter keys")
def sk009_known_keys(skill, ctx):
    unknown = sorted(skill.frontmatter_keys - KNOWN_KEYS)
    if unknown:
        yield _f("SK009", Severity.WARNING, skill,
                 f"unrecognised frontmatter key(s): {', '.join(unknown)}")


@rule("SK010", severity=Severity.ERROR, summary="frontmatter references: paths exist",
      evals_tc="TC1")
def sk010_frontmatter_references_exist(skill, ctx):
    declared = (skill.frontmatter or {}).get("references")
    if not isinstance(declared, list):
        return
    for entry in declared:
        target = str(entry).strip()
        if not (skill.path / target).exists():
            yield _f("SK010", Severity.ERROR, skill,
                     f"frontmatter references: {target!r} does not exist", evals_tc="TC1")
# <AI-Generated END>
