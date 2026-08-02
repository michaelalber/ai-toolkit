# <AI-Generated START>
"""Loading of the reviewable exception files under ``baselines/``.

Every exception here is data, not a code change: a shared state tag or an allowlisted
non-skill name is a decision someone made, and it should be visible next to its written
rationale rather than buried in a rule's implementation.
"""

from __future__ import annotations

from pathlib import Path

import yaml

BASELINE_DIR = Path(__file__).resolve().parent.parent.parent / "baselines"

STATE_TAG_FAMILIES = "state-tag-families.yaml"
KNOWN_NON_SKILLS = "known-non-skills.yaml"


def _read(name: str, repo_root: Path | None = None) -> dict:
    for candidate in _candidates(name, repo_root):
        if candidate.is_file():
            return yaml.safe_load(candidate.read_text()) or {}
    return {}


def _candidates(name: str, repo_root: Path | None):
    if repo_root is not None:
        yield repo_root / "tools" / "skill-evals" / "baselines" / name
    yield BASELINE_DIR / name


def load_state_tag_families(repo_root: Path | None = None) -> dict:
    """``{tag: {"skills": [...], "rationale": "..."}}`` — see SK032."""
    data = _read(STATE_TAG_FAMILIES, repo_root)
    return data.get("families", {}) or {}


def load_known_non_skills(repo_root: Path | None = None) -> set[str]:
    """Backticked names that are legitimately not skills — tools, agents, attributes."""
    data = _read(KNOWN_NON_SKILLS, repo_root)
    return set(data.get("allow", []) or [])
# <AI-Generated END>
