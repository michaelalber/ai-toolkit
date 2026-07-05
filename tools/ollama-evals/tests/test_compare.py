import pytest

from ollama_evals.compare import compare_runs
from ollama_evals.runner import CaseResult, RunResult


def _run(run_id, rows):
    """rows: list of (model, case_id, category, score)."""
    results = [CaseResult(m, cid, cat, s, s == 1.0) for (m, cid, cat, s) in rows]
    manifest = {"run_id": run_id, "models": sorted({r[0] for r in rows})}
    return RunResult(manifest=manifest, results=results)


def test_compare_computes_category_and_overall_deltas():
    base = _run("b", [("old", "c1", "coding", 0.5), ("old", "c2", "chat", 0.8)])
    cand = _run("c", [("new", "c1", "coding", 1.0), ("new", "c2", "chat", 0.8)])
    reg = compare_runs(base, cand, model_baseline="old", model_candidate="new", threshold=0.05)

    assert reg.categories["coding"]["delta"] == pytest.approx(0.5)
    assert reg.categories["chat"]["delta"] == pytest.approx(0.0)
    assert reg.overall["delta"] == pytest.approx(0.25)  # (0.9 - 0.65)
    assert not reg.regressed  # candidate improved overall


def test_regression_flagged_when_category_drops_beyond_threshold():
    base = _run("b", [("old", "c1", "coding", 1.0), ("old", "c2", "chat", 0.5)])
    cand = _run("c", [("new", "c1", "coding", 0.6), ("new", "c2", "chat", 0.9)])
    reg = compare_runs(base, cand, model_baseline="old", model_candidate="new", threshold=0.1)

    assert reg.regressed  # coding fell 0.4, beyond the 0.1 threshold
    assert reg.worst_category == "coding"


def test_no_regression_within_threshold():
    base = _run("b", [("old", "c1", "coding", 1.0)])
    cand = _run("c", [("new", "c1", "coding", 0.97)])
    reg = compare_runs(base, cand, model_baseline="old", model_candidate="new", threshold=0.05)
    assert not reg.regressed


def test_pairwise_win_loss_tie_from_scores():
    base = _run("b", [("old", "c1", "a", 0.0), ("old", "c2", "b", 1.0), ("old", "c3", "c", 0.5)])
    cand = _run("c", [("new", "c1", "a", 1.0), ("new", "c2", "b", 0.0), ("new", "c3", "c", 0.5)])
    reg = compare_runs(base, cand, model_baseline="old", model_candidate="new")
    assert reg.pairwise == {"wins": 1, "losses": 1, "ties": 1}


def test_single_model_runs_infer_model_names():
    base = _run("b", [("old", "c1", "coding", 0.5)])
    cand = _run("c", [("new", "c1", "coding", 1.0)])
    reg = compare_runs(base, cand)  # one model each -> inferred
    assert reg.model_baseline == "old" and reg.model_candidate == "new"


def test_ambiguous_model_selection_raises():
    multi = _run("b", [("a", "c1", "x", 1.0), ("z", "c1", "x", 1.0)])
    with pytest.raises(ValueError):
        compare_runs(multi, multi)
