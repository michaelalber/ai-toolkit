# <AI-Generated START>
"""Rule registry.

Mirrors ollama-evals' scorer registry: a rule declares its id, severity, and scope once,
via decorator, and the linter discovers it. Two scopes exist —

* ``skill`` — runs once per skill, receives ``(skill, ctx)``
* ``repo``  — runs once for the whole corpus, receives ``(skills, ctx)``

A rule returns an iterable of ``Finding`` (or nothing). It never reads files itself; the
``Skill`` model and ``LintContext`` carry everything it needs.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

from ..findings import Severity


@dataclass(frozen=True)
class Rule:
    id: str
    severity: Severity
    scope: str
    summary: str
    fn: Callable
    evals_tc: str | None = None


_REGISTRY: dict[str, Rule] = {}


def rule(
    rule_id: str,
    *,
    severity: Severity,
    scope: str = "skill",
    summary: str = "",
    evals_tc: str | None = None,
) -> Callable:
    def deco(fn: Callable) -> Callable:
        if rule_id in _REGISTRY:
            raise ValueError(f"duplicate rule id: {rule_id}")
        _REGISTRY[rule_id] = Rule(rule_id, severity, scope, summary or fn.__doc__ or "", fn,
                                  evals_tc)
        return fn

    return deco


def all_rules() -> list[Rule]:
    return [_REGISTRY[k] for k in sorted(_REGISTRY)]


def get_rule(rule_id: str) -> Rule:
    try:
        return _REGISTRY[rule_id]
    except KeyError:
        known = ", ".join(sorted(_REGISTRY)) or "(none registered)"
        raise KeyError(f"unknown rule {rule_id!r}; registered: {known}") from None


@dataclass
class LintContext:
    """Everything a rule may need beyond the skill itself."""

    skills: list = field(default_factory=list)
    repo_root: object = None
    state_tag_families: dict = field(default_factory=dict)
    known_non_skills: set = field(default_factory=set)

    @property
    def skill_names(self) -> set[str]:
        return {s.name for s in self.skills}


# Imported for their registration side effects, exactly as ollama-evals does for scorers.
from . import crossref, frontmatter, references, state, structure  # noqa: E402,F401
# <AI-Generated END>
