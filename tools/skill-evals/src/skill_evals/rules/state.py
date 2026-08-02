# <AI-Generated START>
"""SK030-SK033 — state block presence and tag ownership.

Tag uniqueness is scoped to *families*, not to every skill. 31 skills currently share a
tag with a sibling (all six ``*-security-review`` use ``<security-review-state>``, all six
``*-architecture-checklist`` use ``<arch-checklist-state>``), and that is a deliberate
family convention, not drift. What must never happen is two *unrelated* skills claiming
the same tag — a multi-turn session then cannot tell whose state it is reading.

Families are declared in ``baselines/state-tag-families.yaml`` with a written rationale, so
the exception is visible and reviewable rather than implicit.
"""

from __future__ import annotations

import re

from ..findings import Finding, Severity
from ..tier import Tier, classify
from . import rule

_STATE_CLOSE = re.compile(r"</([a-z0-9]+(?:-[a-z0-9]+)*-state)>")


def _f(rule_id, severity, skill, message, *, line=None, evals_tc=None) -> Finding:
    return Finding(rule_id, severity, message, skill.name, skill.skill_md, line, evals_tc)


@rule("SK030", severity=Severity.ERROR, summary="state block present", evals_tc="TC1")
def sk030_state_block_present(skill, ctx):
    if classify(skill) is not Tier.FULL:
        return
    if not skill.state_tags:
        yield _f("SK030", Severity.ERROR, skill,
                 "full-template skill has no <*-state> block", evals_tc="TC1")


@rule("SK031", severity=Severity.ERROR, summary="state tags are balanced", evals_tc="Rubric D5")
def sk031_state_tags_balanced(skill, ctx):
    closed = set(_STATE_CLOSE.findall(skill.text))
    for tag in skill.state_tags:
        if tag not in closed:
            yield _f("SK031", Severity.ERROR, skill,
                     f"<{tag}> is opened but never closed", evals_tc="Rubric D5")


@rule("SK031b", severity=Severity.WARNING, summary="state tag derives from the skill name",
      evals_tc="Rubric D5")
def sk031b_state_tag_related_to_name(skill, ctx):
    name_tokens = set(skill.name.split("-"))
    for tag in skill.state_tags:
        tag_tokens = set(tag.removesuffix("-state").split("-"))
        if not (name_tokens & tag_tokens):
            yield _f("SK031b", Severity.WARNING, skill,
                     f"<{tag}> shares no token with the skill name {skill.name!r}",
                     evals_tc="Rubric D5")


@rule("SK032", severity=Severity.ERROR, scope="repo",
      summary="state tags are owned by one skill or one declared family",
      evals_tc="Taste Rule 3")
def sk032_state_tag_ownership(skills, ctx):
    owners: dict[str, list] = {}
    for skill in skills:
        for tag in skill.state_tags:
            owners.setdefault(tag, []).append(skill)

    for tag, claimants in sorted(owners.items()):
        if len(claimants) < 2:
            continue
        declared = set(ctx.state_tag_families.get(tag, {}).get("skills", []))
        undeclared = [s for s in claimants if s.name not in declared]
        if not declared:
            names = ", ".join(s.name for s in claimants)
            yield Finding(
                "SK032", Severity.ERROR,
                f"<{tag}> is claimed by {len(claimants)} skills ({names}) with no declared "
                "family; add a family entry with a rationale or rename the odd one out",
                skill=claimants[0].name, file=claimants[0].skill_md, evals_tc="Taste Rule 3",
            )
        else:
            for skill in undeclared:
                yield Finding(
                    "SK032", Severity.ERROR,
                    f"<{tag}> belongs to a declared family that does not include {skill.name!r}",
                    skill=skill.name, file=skill.skill_md, evals_tc="Taste Rule 3",
                )


@rule("SK033", severity=Severity.ERROR, scope="repo",
      summary="skill state tags do not collide with agent state tags", evals_tc="TC2")
def sk033_no_agent_tag_collision(skills, ctx):
    """An agent's tag must stay distinct from the skill it defers to.

    ``code-review-agent`` and ``automated-code-review`` are the canonical example: the
    agent keeps ``<code-review-state>`` precisely because the skill owns
    ``<automated-review-state>``.
    """
    root = ctx.repo_root
    if root is None:
        return
    skill_owner = {tag: s.name for s in skills for tag in s.state_tags}
    for agent_dir in ("claude/agents", "opencode/agents"):
        base = root / agent_dir
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*.md")):
            text = path.read_text()
            for tag in set(re.findall(r"<([a-z0-9]+(?:-[a-z0-9]+)*-state)>", text)):
                owner = skill_owner.get(tag)
                if owner and owner != path.stem:
                    platform = agent_dir.split("/")[0]
                    yield Finding(
                        "SK033", Severity.ERROR,
                        f"{platform} agent {path.stem!r} uses <{tag}>, already owned by skill "
                        f"{owner!r}",
                        skill=owner, file=path, evals_tc="TC2",
                    )
# <AI-Generated END>
