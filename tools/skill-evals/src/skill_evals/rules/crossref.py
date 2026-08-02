# <AI-Generated START>
"""SK050-SK059 — cross-reference and repo-metadata integrity.

These replace the six manual grep bullets in ``evals.md``'s CI Gate, including the one
that never worked. Metadata drift is the repo's most common regression: a skill is added
or renamed, and the README badge, the at-a-glance table, the Pi triage doc, and the two
context files fall out of sync one at a time, silently.

Nothing here hardcodes a corpus size. Every count is compared against the tree.
"""

from __future__ import annotations

import difflib

from ..findings import Finding, Severity
from ..repo import agent_names, count_claims, parse_pi_triage, parse_readme
from . import rule

PI_TRIAGE = "pi/SKILLS-local.md"
CONTEXT_FILES = ("CLAUDE.md", "AGENTS.md")

# A backticked slug is only worth reporting when it looks like a *stale skill name* rather
# than one of the many tools and attributes the corpus legitimately name-drops.
_SIMILARITY = 0.72


def _repo_finding(rule_id, message, *, file=None, line=None, skill=None, evals_tc=None):
    return Finding(rule_id, Severity.ERROR, message, skill, file, line, evals_tc)


@rule("SK050", severity=Severity.ERROR, summary="Integration targets resolve to real skills",
      evals_tc="TC7")
def sk050_integration_targets_resolve(skill, ctx):
    """Only the Integration table's first column — the relationship column name-drops."""
    for target in skill.integration_targets:
        if target in ctx.skill_names or target in ctx.known_non_skills:
            continue
        suggestion = _closest(target, ctx.skill_names)
        hint = f"; did you mean {suggestion!r}?" if suggestion else ""
        yield Finding("SK050", Severity.ERROR,
                      f"Integration table names `{target}`, which is not a skill{hint}",
                      skill.name, skill.skill_md, None, "TC7")


@rule("SK051", severity=Severity.WARNING, scope="repo",
      summary="Integration cross-references are symmetric", evals_tc="TC7")
def sk051_integration_symmetry(skills, ctx):
    by_name = {s.name: s for s in skills}
    for skill in skills:
        for target in skill.integration_targets:
            other = by_name.get(target)
            if other is None or not other.has_section("Integration"):
                # A minimal-tier skill has no Integration section by design; demanding
                # reciprocity from it would be asking for a section it must not have.
                continue
            if skill.name not in other.integration_targets:
                yield Finding("SK051", Severity.WARNING,
                              f"names `{target}` in Integration, but `{target}` does not name "
                              f"`{skill.name}` back",
                              skill.name, skill.skill_md, None, "TC7")


@rule("SK052", severity=Severity.WARNING, summary="backticked skill-like names resolve",
      evals_tc="TC7")
def sk052_stale_skill_references(skill, ctx):
    """Catches a rename's long tail: prose still naming the old skill.

    Reported only when the token closely resembles a real skill name, so the many
    backticked tools (`cargo-audit`, `pip-audit`) and attributes (`v-html`) stay quiet.

    Scope note: only *hyphenated* tokens are considered. A single word would prefix-match
    far too eagerly — a backticked `python` would "resemble" python-feature-slice — and the
    resulting noise would bury the real hits. Single-word stale names still get caught by
    SK050 wherever they appear in an Integration table, which is where they do damage.
    """
    for token in sorted(skill.backticked_slugs):
        if token in ctx.skill_names or token in ctx.known_non_skills or token == skill.name:
            continue
        suggestion = _closest(token, ctx.skill_names)
        if suggestion:
            yield Finding("SK052", Severity.WARNING,
                          f"`{token}` is not a skill; closest is `{suggestion}` — stale rename?",
                          skill.name, skill.skill_md, None, "TC7")


@rule("SK053", severity=Severity.ERROR, scope="repo",
      summary="every skill is triaged in pi/SKILLS-local.md", evals_tc="CI Gate")
def sk053_pi_triage_covers_every_skill(skills, ctx):
    triage = parse_pi_triage(ctx.repo_root / PI_TRIAGE)
    if not triage.present:
        return
    listed = set(triage.all_names)
    for skill in skills:
        if skill.name not in listed:
            yield Finding("SK053", Severity.ERROR,
                          f"no Green/Yellow/Red row in {PI_TRIAGE}",
                          skill.name, skill.skill_md, None, "CI Gate")


@rule("SK054", severity=Severity.ERROR, scope="repo",
      summary="every pi triage row names a real skill", evals_tc="constraints.md")
def sk054_pi_triage_rows_resolve(skills, ctx):
    triage = parse_pi_triage(ctx.repo_root / PI_TRIAGE)
    if not triage.present:
        return
    path = ctx.repo_root / PI_TRIAGE
    for name in triage.all_names:
        if name not in ctx.skill_names:
            suggestion = _closest(name, ctx.skill_names)
            hint = f"; did you mean {suggestion!r}?" if suggestion else ""
            yield _repo_finding("SK054", f"{PI_TRIAGE} lists `{name}`, which is not a skill{hint}",
                                file=path, evals_tc="constraints.md")


@rule("SK055", severity=Severity.ERROR, scope="repo",
      summary="pi triage counts agree with its own rows", evals_tc="TC4")
def sk055_pi_triage_counts_agree(skills, ctx):
    triage = parse_pi_triage(ctx.repo_root / PI_TRIAGE)
    if not triage.present:
        return
    path = ctx.repo_root / PI_TRIAGE
    rows = triage.row_counts()

    for tier, declared in triage.declared_header_counts.items():
        actual = rows.get(tier, 0)
        if declared != actual:
            yield _repo_finding("SK055",
                                f"{PI_TRIAGE} {tier} heading claims {declared} but has {actual} "
                                "rows", file=path, evals_tc="TC4")

    footer = triage.declared_footer_counts
    if footer is None:
        return
    order = ["🟢", "🟡", "🔴"]
    for tier, declared in zip(order, footer[:3], strict=False):
        actual = rows.get(tier, 0)
        if declared != actual:
            yield _repo_finding("SK055",
                                f"{PI_TRIAGE} footer claims {declared} {tier} but there are "
                                f"{actual}", file=path, evals_tc="TC4")
    total_rows = sum(rows.values())
    if footer[3] != total_rows:
        yield _repo_finding("SK055",
                            f"{PI_TRIAGE} footer total is {footer[3]} but there are "
                            f"{total_rows} rows ({len(skills)} skills exist)",
                            file=path, evals_tc="TC4")


@rule("SK056", severity=Severity.ERROR, scope="repo",
      summary="README lists every skill exactly once", evals_tc="TC4, TC7")
def sk056_readme_lists_every_skill(skills, ctx):
    readme = ctx.repo_root / "README.md"
    index = parse_readme(readme)
    if not index.present:
        return
    listed = index.all_names
    seen = set(listed)

    for skill in skills:
        if skill.name not in seen:
            yield Finding("SK056", Severity.ERROR,
                          "not listed in any README skill table",
                          skill.name, skill.skill_md, None, "TC4")

    for name in sorted(seen - ctx.skill_names):
        suggestion = _closest(name, ctx.skill_names)
        hint = f"; did you mean {suggestion!r}?" if suggestion else ""
        yield _repo_finding("SK056", f"README lists `{name}`, which is not a skill{hint}",
                            file=readme, evals_tc="TC7")

    for name in sorted({n for n in listed if listed.count(n) > 1}):
        yield _repo_finding("SK056", f"README lists `{name}` in more than one suite table",
                            file=readme, evals_tc="TC4")


@rule("SK057", severity=Severity.ERROR, scope="repo",
      summary="published counts match the tree", evals_tc="TC4")
def sk057_counts_match_reality(skills, ctx):
    root = ctx.repo_root
    actual_skills = len(skills)
    actual_agents = len(agent_names(root, "claude"))

    readme = root / "README.md"
    index = parse_readme(readme)
    if index.present:
        for label, claimed, actual in (
            ("badge", index.badge_skills, actual_skills),
            ("intro prose", index.prose_skills, actual_skills),
            ("at-a-glance", index.glance_skill_total, actual_skills),
        ):
            if claimed is not None and claimed != actual:
                yield _repo_finding("SK057",
                                    f"README {label} claims {claimed} skills; there are {actual}",
                                    file=readme, evals_tc="TC4")
        for label, claimed in (("badge", index.badge_agents), ("intro prose", index.prose_agents)):
            if claimed is not None and claimed != actual_agents:
                yield _repo_finding("SK057",
                                    f"README {label} claims {claimed} agents; there are "
                                    f"{actual_agents}", file=readme, evals_tc="TC4")
        for label in ("Agents (Claude Code)", "Agents (OpenCode)"):
            claimed = index.glance.get(label)
            platform = "claude" if "Claude" in label else "opencode"
            actual = len(agent_names(root, platform))
            if claimed is not None and claimed != actual:
                yield _repo_finding("SK057",
                                    f"README at-a-glance claims {claimed} for {label!r}; there "
                                    f"are {actual}", file=readme, evals_tc="TC4")

    for name in CONTEXT_FILES:
        path = root / name
        for lineno, claimed in count_claims(path):
            if claimed != actual_skills:
                yield _repo_finding("SK057",
                                    f"{name} claims {claimed} skills; there are {actual_skills}",
                                    file=path, line=lineno, evals_tc="TC4")


@rule("SK058", severity=Severity.ERROR, scope="repo",
      summary="Claude and OpenCode agents are in parity", evals_tc="TC2")
def sk058_agent_parity(skills, ctx):
    root = ctx.repo_root
    claude, opencode = agent_names(root, "claude"), agent_names(root, "opencode")
    if not claude and not opencode:
        return
    for name in sorted(claude - opencode):
        yield _repo_finding("SK058", f"agent {name!r} exists for Claude Code but not OpenCode",
                            file=root / "opencode" / "agents", evals_tc="TC2")
    for name in sorted(opencode - claude):
        yield _repo_finding("SK058", f"agent {name!r} exists for OpenCode but not Claude Code",
                            file=root / "claude" / "agents", evals_tc="TC2")


@rule("SK059", severity=Severity.ERROR, scope="repo",
      summary="CLAUDE.md and AGENTS.md are byte-identical", evals_tc="Editing Guidelines")
def sk059_context_mirror_pair(skills, ctx):
    """Whichever agent opens the project must get the same project context."""
    root = ctx.repo_root
    claude_md, agents_md = root / "CLAUDE.md", root / "AGENTS.md"
    if not (claude_md.is_file() and agents_md.is_file()):
        return
    left, right = claude_md.read_bytes(), agents_md.read_bytes()
    if left != right:
        diff = list(difflib.unified_diff(
            left.decode(errors="replace").splitlines(),
            right.decode(errors="replace").splitlines(),
            lineterm="", n=0,
        ))
        changed = sum(1 for line in diff if line.startswith(("+", "-")) and line[1:2] != "-")
        yield _repo_finding("SK059",
                            f"CLAUDE.md and AGENTS.md differ ({changed} changed line(s)) — "
                            "they are a mirror pair; edit both",
                            file=claude_md, evals_tc="Editing Guidelines")


def _closest(name: str, candidates: set[str]) -> str | None:
    """The likeliest intended skill, or None.

    A hyphen-boundary prefix relation is checked first because that is what a rename
    actually looks like — `tdd` -> `tdd-loop`. Pure string similarity misses it: those two
    score 0.55, well under any cutoff loose enough to stay quiet on unrelated names.
    """
    prefixed = [
        c for c in sorted(candidates)
        if c.startswith(f"{name}-") or name.startswith(f"{c}-")
    ]
    if prefixed:
        # `tdd` prefix-matches both tdd-agent and tdd-loop; rank by similarity so the
        # suggestion is the nearest name, not the alphabetically first one.
        return max(prefixed, key=lambda c: (difflib.SequenceMatcher(None, name, c).ratio(), c))
    matches = difflib.get_close_matches(name, sorted(candidates), n=1, cutoff=_SIMILARITY)
    return matches[0] if matches else None
# <AI-Generated END>
