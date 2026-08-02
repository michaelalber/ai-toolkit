# <AI-Generated START>
"""The skill roster the routing eval puts in front of the model.

Built from the live corpus at run time, never committed, so it cannot go stale against the
tree it describes. Its sha256 goes into the run manifest: a roster change then visibly
invalidates a baseline comparison instead of silently shifting the numbers.

The full roster of 94 name+description pairs is roughly 38K characters — about 9.5K tokens,
above ollama-evals' default `num_ctx` of 8192. That is why `models.yaml` here ships 32768,
and why a `shard` mode exists for endpoints that cannot serve it.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass

FULL = "full"
SHARD = "shard"
TRUNCATED = "truncated"
MODES = (FULL, SHARD, TRUNCATED)

_SENTENCE = re.compile(r"(?<=[.!?])\s+")

INSTRUCTION = (
    "You route user requests to skills. Below is every available skill and what it does.\n\n"
    "{roster}\n\n"
    "Given the user's message, choose the ONE skill that should handle it. If no skill "
    "fits, answer \"none\" — do not force a match.\n"
    "Reply with ONLY a JSON object:\n"
    '{{"skill": "<name>|none", "runner_up": "<name>|none"}}'
)


@dataclass(frozen=True)
class Roster:
    text: str
    names: tuple[str, ...]
    mode: str
    withheld: tuple[str, ...] = ()
    """Skills excluded because they set ``disable-model-invocation``."""

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.text.encode()).hexdigest()

    def system_prompt(self) -> str:
        return INSTRUCTION.format(roster=self.text)


def build(skills, mode: str = FULL, *, shards: int = 3, shard_index: int = 0,
          must_include: str | None = None, include_non_invocable: bool = False) -> Roster:
    """Render the roster the model sees.

    Skills with ``disable-model-invocation: true`` are withheld by default, because that
    is what the harness does: the model is never offered them, so putting them in the
    roster would measure a scenario that cannot occur and report a "breach" for behaviour
    the flag already prevents.

    ``must_include`` guarantees the expected skill is present in a shard — without it a
    sharded run would score a case the model could not possibly have got right.
    """
    if mode not in MODES:
        raise ValueError(f"unknown roster mode {mode!r}; use one of {list(MODES)}")

    ordered = sorted(skills, key=lambda s: s.name)
    withheld: tuple[str, ...] = ()
    if not include_non_invocable:
        blocked = [s for s in ordered if is_non_invocable(s)]
        withheld = tuple(s.name for s in blocked)
        ordered = [s for s in ordered if not is_non_invocable(s)]

    entries = _shard(ordered, shards, shard_index, must_include) if mode == SHARD else ordered
    lines = [f"- {s.name}: {_describe(s, mode)}" for s in entries]
    return Roster(
        text="\n".join(lines),
        names=tuple(s.name for s in entries),
        mode=mode,
        withheld=withheld,
    )


def is_non_invocable(skill) -> bool:
    value = (skill.frontmatter or {}).get("disable-model-invocation")
    return str(value).strip().lower() == "true"


def _describe(skill, mode: str) -> str:
    description = " ".join(skill.description.split())
    if mode != TRUNCATED:
        return description
    # Two sentences drops the "Do NOT use when ..." clause. The accuracy delta between
    # `full` and `truncated` IS the measurement of what negative boundaries buy.
    return " ".join(_SENTENCE.split(description)[:2])


def _shard(entries, shards: int, index: int, must_include: str | None):
    if shards < 1:
        raise ValueError("shards must be >= 1")
    index %= shards
    # Deterministic by position in the sorted corpus — no RNG, so a rerun is identical.
    selected = [s for i, s in enumerate(entries) if i % shards == index]
    if must_include and must_include not in {s.name for s in selected}:
        extra = next((s for s in entries if s.name == must_include), None)
        if extra is not None:
            selected = sorted([*selected, extra], key=lambda s: s.name)
    return selected


def candidate_pairs(skills, top: int = 15) -> list[tuple[str, str, float]]:
    """Skill pairs most likely to be confused, ranked by description similarity.

    Which pairs are worth writing a confusion case for is a measurement, not a matter of
    taste — this ranks all C(n,2) by trigram Jaccard over their descriptions.
    """
    profiles = [(s.name, _trigrams(s.description)) for s in sorted(skills, key=lambda s: s.name)]
    scored: list[tuple[str, str, float]] = []
    for i, (name_a, tri_a) in enumerate(profiles):
        for name_b, tri_b in profiles[i + 1 :]:
            union = tri_a | tri_b
            if not union:
                continue
            scored.append((name_a, name_b, len(tri_a & tri_b) / len(union)))
    scored.sort(key=lambda row: (-row[2], row[0], row[1]))
    return scored[:top]


def _trigrams(text: str) -> set[str]:
    normalised = re.sub(r"[^a-z0-9 ]+", " ", text.lower())
    normalised = " ".join(normalised.split())
    return {normalised[i : i + 3] for i in range(max(0, len(normalised) - 2))}
# <AI-Generated END>
