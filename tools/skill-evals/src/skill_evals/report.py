# <AI-Generated START>
"""Render lint findings as text, JSON, or Markdown.

Text is the default because the primary consumer is a human at a terminal about to commit.
JSON exists so a finding set can be diffed or snapshotted into a baseline.
"""

from __future__ import annotations

import json

from .findings import FindingSet, Severity
from .rules import get_rule

_ICON = {Severity.ERROR: "✗", Severity.WARNING: "!"}


def to_text(findings: FindingSet, *, total_skills: int = 0) -> str:
    lines: list[str] = []
    current_rule = None
    for f in findings.sorted():
        if f.rule_id != current_rule:
            current_rule = f.rule_id
            summary = _summary(f.rule_id)
            lines.append("")
            lines.append(f"{f.severity.value.upper()} {f.rule_id} — {summary}")
        lines.append(f"  {_ICON[f.severity]} {f.location}")
        lines.append(f"      {f.message}")
    lines.append("")
    lines.append(_summary_line(findings, total_skills))
    return "\n".join(lines).lstrip("\n")


def to_markdown(findings: FindingSet, *, total_skills: int = 0) -> str:
    lines = ["# Skill lint", "", _summary_line(findings, total_skills), ""]
    grouped = findings.by_rule()
    if not grouped:
        return "\n".join(lines)
    lines += ["| Rule | Severity | Skill | Location | Finding |", "|---|---|---|---|---|"]
    for f in findings.sorted():
        lines.append(
            f"| `{f.rule_id}` | {f.severity.value} | `{f.skill or '—'}` | "
            f"`{f.location}` | {f.message} |"
        )
    return "\n".join(lines)


def to_json(findings: FindingSet, *, total_skills: int = 0) -> str:
    payload = {
        "total_skills": total_skills,
        "errors": len(findings.errors),
        "warnings": len(findings.warnings),
        "findings": [
            {
                "rule": f.rule_id,
                "severity": f.severity.value,
                "skill": f.skill,
                "file": str(f.file) if f.file else None,
                "line": f.line,
                "message": f.message,
                "evals_tc": f.evals_tc,
            }
            for f in findings.sorted()
        ],
    }
    return json.dumps(payload, indent=2)


def routing_to_text(result, *, show_confusion: bool = False) -> str:
    s = result.summary
    lines = [
        "# Routing eval",
        "",
        f"roster:          {result.roster_mode} ({result.run.manifest.get('roster_size', '?')} "
        f"skills, sha {result.roster_sha[:12]})",
        f"withheld:        {len(result.run.manifest.get('roster_withheld', []))} "
        "disable-model-invocation skills, as the harness does",
        f"top-1 accuracy:  {s.accuracy:.2f}  ({s.exact}/{s.total - s.parse_failures} scoreable)",
        f"top-2 accuracy:  {s.top2_accuracy:.2f}",
        f"missed:          {s.missed}",
        f"parse failures:  {s.parse_failures}"
        + ("  ← the endpoint, not the skills" if s.parse_failures else ""),
    ]

    if result.collisions:
        lines += ["", "## Description collisions", "",
                  "| Expected | Chosen instead | Rate |", "|---|---|---|"]
        lines += [
            f"| `{c.expected}` | `{c.chosen}` | {c.rate:.0%} ({c.count}/{c.total}) |"
            for c in result.collisions
        ]
    else:
        lines += ["", "No description collisions above the threshold."]

    if result.breaches:
        lines += ["", "## disable-model-invocation breaches", ""]
        lines += [f"- `{name}` was auto-selected" for name in result.breaches]

    if show_confusion:
        lines += ["", "## Confusion matrix", ""]
        for expected in sorted(result.confusion):
            chosen = result.confusion[expected]
            row = ", ".join(f"{k}×{v}" for k, v in chosen.most_common())
            lines.append(f"- `{expected}` → {row}")

    return "\n".join(lines)


def scorecard_to_text(result, *, limit: int | None = None) -> str:
    s = result.summary
    lines = [
        "# Skill rubric scorecard",
        "",
        f"skills scored:   {s['n_skills']}",
        f"mean total:      {s['mean_total']:.1f} / {s['max_total']}",
        f"median total:    {s['median_total']:.1f} / {s['max_total']}",
        f"judge calls:     {s['n_dimension_calls']}",
        f"parse failures:  {s['parse_failures']}"
        + ("  ← the judge, not the skills" if s["parse_failures"] else ""),
        "",
        "| Verdict | Count |",
        "|---|---|",
    ]
    for verdict in ("EXEMPLARY", "PASS", "REVISE", "DEPRECATE", "INCOMPLETE"):
        if verdict in s["verdicts"]:
            lines.append(f"| {verdict} | {s['verdicts'][verdict]} |")

    ranked = sorted(result.scores, key=lambda x: (x.incomplete, x.total))
    shown = ranked[:limit] if limit else ranked
    lines += ["", f"## Skills, weakest first{f' (lowest {limit})' if limit else ''}", "",
              "| Skill | Total | Verdict | Weakest dimension |", "|---|---|---|---|"]
    for score in shown:
        weakest = min(score.scored, key=lambda d: d.score, default=None)
        weak = f"{weakest.name} ({weakest.score:.0f})" if weakest else "—"
        lines.append(
            f"| `{score.skill}` | {score.total:.0f}/{s['max_total']} | "
            f"{score.verdict(result.rubric)} | {weak} |"
        )
    return "\n".join(lines)


def quality_to_text(result) -> str:
    rows = result.rows
    lines = [
        "# Skill output quality",
        "",
        f"cases:           {len(rows)}",
        f"passed:          {sum(1 for r in rows if r.passed)}",
        f"parse failures:  {sum(1 for r in rows if (r.metadata or {}).get('parse_failure'))}",
        "",
        "| Case | Score | Pass | State block | Phases missing | Hallucinated refs |",
        "|---|---|---|---|---|---|",
    ]
    for r in sorted(rows, key=lambda r: r.score):
        structural = (r.metadata or {}).get("structural") or {}
        missing = ", ".join(structural.get("phases_missing") or []) or "—"
        hallucinated = ", ".join(structural.get("hallucinated_references") or []) or "—"
        emitted = structural.get("emitted_state_block")
        lines.append(
            f"| `{r.case_id}` | {r.score:.2f} | {'yes' if r.passed else 'NO'} | "
            f"{'yes' if emitted else 'no' if emitted is False else '—'} | {missing} | "
            f"{hallucinated} |"
        )

    weak = [r for r in rows if not r.passed]
    if weak:
        lines += ["", "## Weakest criterion per failing case", ""]
        for r in weak:
            per = (r.metadata or {}).get("per_criterion") or []
            if per:
                worst = min(per, key=lambda c: c["score"])
                lines.append(f"- `{r.case_id}` — {worst['criterion']} ({worst['score']:.2f})")
    return "\n".join(lines)


def _summary_line(findings: FindingSet, total_skills: int) -> str:
    n_err, n_warn = len(findings.errors), len(findings.warnings)
    scope = f"{total_skills} skills" if total_skills else "corpus"
    if not n_err and not n_warn:
        return f"clean — {scope}, no findings"
    return f"{scope}: {n_err} error(s), {n_warn} warning(s)"


def _summary(rule_id: str) -> str:
    try:
        return get_rule(rule_id).summary.strip().splitlines()[0]
    except (KeyError, IndexError):
        return ""
# <AI-Generated END>
