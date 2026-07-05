# <AI-Generated START>
"""Compare two runs: per-category deltas, pairwise win/loss/tie, and a regression gate.

The core "is the new model as good as the old one?" answer. A run may hold several models,
so ``compare_runs`` selects one model from each side (inferred when a run has exactly one).
Pairwise is computed from per-case scores — deterministic and judge-free.
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass


@dataclass
class RegressionReport:
    model_baseline: str
    model_candidate: str
    categories: dict  # category -> {"baseline", "candidate", "delta"}
    overall: dict  # {"baseline", "candidate", "delta"}
    pairwise: dict  # candidate's view: {"wins", "losses", "ties"}
    threshold: float
    regressed: bool
    worst_category: str | None


def _models_in(run) -> list[str]:
    return sorted({r.model for r in run.results})


def _select_model(run, model: str | None) -> str:
    if model is not None:
        return model
    models = _models_in(run)
    if len(models) == 1:
        return models[0]
    raise ValueError(f"run holds multiple models {models}; pass the model name explicitly")


def _category_means(run, model: str) -> dict[str, float]:
    by_cat: dict[str, list[float]] = {}
    for r in run.results:
        if r.model == model:
            by_cat.setdefault(r.category, []).append(r.score)
    return {c: statistics.mean(v) for c, v in by_cat.items()}


def _overall(run, model: str) -> float:
    scores = [r.score for r in run.results if r.model == model]
    return statistics.mean(scores) if scores else 0.0


def _scores_by_case(run, model: str) -> dict[str, float]:
    return {r.case_id: r.score for r in run.results if r.model == model}


def compare_runs(
    baseline,
    candidate,
    *,
    model_baseline: str | None = None,
    model_candidate: str | None = None,
    threshold: float = 0.05,
) -> RegressionReport:
    mb = _select_model(baseline, model_baseline)
    mc = _select_model(candidate, model_candidate)

    base_cat = _category_means(baseline, mb)
    cand_cat = _category_means(candidate, mc)
    categories: dict[str, dict] = {}
    for cat in sorted(set(base_cat) | set(cand_cat)):
        b = base_cat.get(cat)
        c = cand_cat.get(cat)
        delta = c - b if (b is not None and c is not None) else None
        categories[cat] = {"baseline": b, "candidate": c, "delta": delta}

    ob, oc = _overall(baseline, mb), _overall(candidate, mc)
    overall = {"baseline": ob, "candidate": oc, "delta": oc - ob}

    bs, cs = _scores_by_case(baseline, mb), _scores_by_case(candidate, mc)
    wins = losses = ties = 0
    for cid in set(bs) & set(cs):
        if cs[cid] > bs[cid]:
            wins += 1
        elif cs[cid] < bs[cid]:
            losses += 1
        else:
            ties += 1
    pairwise = {"wins": wins, "losses": losses, "ties": ties}

    cat_deltas = [(c, v["delta"]) for c, v in categories.items() if v["delta"] is not None]
    regressed = overall["delta"] < -threshold
    worst_category = None
    if cat_deltas:
        worst_cat, worst_delta = min(cat_deltas, key=lambda x: x[1])
        if worst_delta < -threshold:
            regressed = True
            worst_category = worst_cat
        elif regressed:  # overall regressed even if no single category tripped the gate
            worst_category = worst_cat

    return RegressionReport(
        mb, mc, categories, overall, pairwise, threshold, regressed, worst_category
    )
# <AI-Generated END>
