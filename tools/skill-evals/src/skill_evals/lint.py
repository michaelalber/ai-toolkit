# <AI-Generated START>
"""Rule orchestration.

Loads the corpus once, builds a shared context, runs every registered rule, and applies
the baseline. Rules never read files or know about each other.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from .corpus import discover
from .findings import Finding, FindingSet, Severity
from .rules import LintContext, all_rules, get_rule


def load_baseline(path: str | Path | None) -> set[tuple]:
    """Read accepted findings from a baseline YAML into a set of ``Finding.key()``."""
    if not path:
        return set()
    path = Path(path)
    if not path.exists():
        return set()
    data = yaml.safe_load(path.read_text()) or {}
    return {
        (entry.get("rule"), entry.get("skill"), entry.get("message", ""))
        for entry in data.get("accepted", [])
    }


def dump_baseline(findings: FindingSet, note: str = "", repo_root: Path | None = None) -> str:
    """Serialise findings as a baseline document (used to snapshot known defects).

    Paths are written relative to the repo root so a baseline is portable between
    checkouts — an absolute path would match nothing on anyone else's machine.
    """
    accepted = [
        {
            "rule": f.rule_id,
            "skill": f.skill,
            "file": _relative(f.file, repo_root),
            "message": f.message,
        }
        for f in findings.sorted()
    ]
    return yaml.safe_dump(
        {"note": note, "accepted": accepted}, sort_keys=False, default_flow_style=False
    )


def evidence_for(skill, ctx: LintContext | None = None) -> dict:
    """Measured facts about a skill, for the rubric judge to reason *from*.

    Several rubric dimensions are largely mechanical — line count, section list, reference
    files, tag collisions. Asking a local model to count those is the single biggest source
    of run-to-run variance, so they are measured here and handed over as evidence. The
    judge then only does the part that needs judgement.
    """
    from .tier import classify

    tag_owners: dict[str, list[str]] = {}
    for other in (ctx.skills if ctx else [skill]):
        for tag in other.state_tags:
            tag_owners.setdefault(tag, []).append(other.name)

    shared = sorted({
        tag for tag in skill.state_tags if len(tag_owners.get(tag, [])) > 1
    })
    families = (ctx.state_tag_families if ctx else {}) or {}

    return {
        "name": skill.name,
        "tier": classify(skill).value,
        "line_count": skill.line_count,
        "sections": list(skill.sections),
        "description_chars": len(skill.description),
        "has_trigger_clause": any(
            m in skill.description.lower() for m in ("use when", "use for", "triggers on")
        ),
        "has_negative_boundary": any(
            m in skill.description.lower() for m in ("do not use", "not for", "not when")
        ),
        "state_tags": list(skill.state_tags),
        "state_tag_shared_with": {t: tag_owners[t] for t in shared},
        "state_tag_declared_family": [t for t in shared if t in families],
        "reference_files": [
            f"{p.relative_to(skill.path).as_posix()} ({len(p.read_text().splitlines())} lines)"
            for p in skill.reference_files
            if p.suffix == ".md"
        ],
        "reference_pointers": sorted({p.target for p in skill.reference_pointers}),
        "unresolved_pointers": sorted({
            p.target for p in skill.reference_pointers if not (skill.path / p.target).exists()
        }),
        "integration_targets": list(skill.integration_targets),
    }


def _relative(path: Path | None, repo_root: Path | None) -> str:
    if path is None:
        return ""
    if repo_root is not None:
        try:
            return path.relative_to(repo_root).as_posix()
        except ValueError:
            pass
    return str(path)


def build_context(
    skills,
    repo_root: Path | None = None,
    state_tag_families: dict | None = None,
    known_non_skills: set | None = None,
) -> LintContext:
    return LintContext(
        skills=skills,
        repo_root=repo_root,
        state_tag_families=state_tag_families or {},
        known_non_skills=known_non_skills or set(),
    )


def lint(
    skills_dir: str | Path,
    *,
    repo_root: str | Path | None = None,
    only: list[str] | None = None,
    baseline: str | Path | None = None,
    state_tag_families: dict | None = None,
    known_non_skills: set | None = None,
) -> FindingSet:
    skills = discover(skills_dir)
    ctx = build_context(
        skills,
        repo_root=Path(repo_root) if repo_root else Path(skills_dir).parent,
        state_tag_families=state_tag_families,
        known_non_skills=known_non_skills,
    )
    rules = [get_rule(r) for r in only] if only else all_rules()

    results = FindingSet()
    for r in rules:
        if r.scope == "repo":
            results.extend(_run(r, r.fn, skills, ctx))
        else:
            for skill in skills:
                results.extend(_run(r, r.fn, skill, ctx))
    return results.without(load_baseline(baseline))


def _run(rule, fn, target, ctx):
    """Run one rule, converting a crash into a finding rather than aborting the lint."""
    try:
        return list(fn(target, ctx) or [])
    except Exception as exc:  # noqa: BLE001 - one broken rule must not hide the rest
        skill_name = getattr(target, "name", None) if not isinstance(target, list) else None
        return [
            Finding(
                rule_id=rule.id,
                severity=Severity.ERROR,
                message=f"rule crashed: {exc!r}",
                skill=skill_name,
            )
        ]
# <AI-Generated END>
