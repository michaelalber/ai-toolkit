# <AI-Generated START>
"""Scorer contract and registry.

A scorer maps a model output + a case's scorer spec to a ``ScoreResult`` in [0, 1].
Scorers register themselves by a ``type`` string; cases select one via ``{"type": ...}``.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

# A scorer receives (output, spec, context) and returns a ScoreResult.
Scorer = Callable[[str, dict, dict], "ScoreResult"]

_REGISTRY: dict[str, Scorer] = {}


@dataclass
class ScoreResult:
    score: float  # 0.0–1.0
    passed: bool
    detail: str = ""
    metadata: dict = field(default_factory=dict)


def register(name: str) -> Callable[[Scorer], Scorer]:
    def deco(fn: Scorer) -> Scorer:
        _REGISTRY[name] = fn
        return fn

    return deco


def get_scorer(name: str) -> Scorer:
    return _REGISTRY[name]


def score_output(output: str, spec: dict, context: dict | None = None) -> ScoreResult:
    """Dispatch to the scorer named by ``spec['type']``."""
    scorer = get_scorer(spec["type"])
    return scorer(output, spec, context or {})
# <AI-Generated END>
