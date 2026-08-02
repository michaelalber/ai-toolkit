# <AI-Generated START>
"""Aggregation for the routing eval: accuracy, confusion matrix, collision pairs.

The deliverable is `collisions()` — the ordered pairs the model actually confuses. That is
the empirical answer to "do these descriptions overlap", as opposed to reading 94
descriptions and forming an opinion.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass


@dataclass(frozen=True)
class Collision:
    expected: str
    chosen: str
    count: int
    total: int

    @property
    def rate(self) -> float:
        return self.count / self.total if self.total else 0.0


@dataclass(frozen=True)
class RoutingSummary:
    total: int
    exact: int
    runner_up: int
    missed: int
    parse_failures: int

    @property
    def accuracy(self) -> float:
        """Top-1 accuracy over *scoreable* cases — parse failures are excluded.

        A broken endpoint must not read as poor skill descriptions.
        """
        scoreable = self.total - self.parse_failures
        return self.exact / scoreable if scoreable else 0.0

    @property
    def top2_accuracy(self) -> float:
        scoreable = self.total - self.parse_failures
        return (self.exact + self.runner_up) / scoreable if scoreable else 0.0

    @property
    def parse_failure_rate(self) -> float:
        return self.parse_failures / self.total if self.total else 0.0


def summarise(results) -> RoutingSummary:
    total = exact = runner_up = missed = parse_failures = 0
    for r in _routing_results(results):
        total += 1
        meta = r.metadata or {}
        if meta.get("parse_failure"):
            parse_failures += 1
        elif r.score >= 1.0:
            exact += 1
        elif r.score > 0.0:
            runner_up += 1
        else:
            missed += 1
    return RoutingSummary(total, exact, runner_up, missed, parse_failures)


def confusion_matrix(results) -> dict[str, Counter]:
    """``{expected: Counter({chosen: n})}`` over every scoreable routing result."""
    matrix: dict[str, Counter] = defaultdict(Counter)
    for r in _routing_results(results):
        meta = r.metadata or {}
        if meta.get("parse_failure"):
            continue
        expected = meta.get("expected") or "none"
        chosen = meta.get("chosen") or "none"
        matrix[expected][chosen] += 1
    return dict(matrix)


def collisions(results, threshold: float = 0.2) -> list[Collision]:
    """Ordered pairs mis-selected at or above ``threshold`` — the collision report."""
    found: list[Collision] = []
    for expected, chosen_counts in confusion_matrix(results).items():
        total = sum(chosen_counts.values())
        for chosen, count in chosen_counts.items():
            if chosen == expected:
                continue
            if total and count / total >= threshold:
                found.append(Collision(expected, chosen, count, total))
    found.sort(key=lambda c: (-c.rate, c.expected, c.chosen))
    return found


def never_auto_selected(results, names) -> list[str]:
    """Of ``names``, those the model DID auto-select — a disable-model-invocation breach."""
    chosen = {
        (r.metadata or {}).get("chosen")
        for r in _routing_results(results)
    }
    return sorted(n for n in names if n in chosen)


def _routing_results(results):
    rows = getattr(results, "results", results)
    return [r for r in rows if r.category == "routing"]
# <AI-Generated END>
