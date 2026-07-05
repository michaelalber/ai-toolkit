from ollama_evals.compare import compare_runs
from ollama_evals.report import comparison_to_html, comparison_to_markdown, run_to_markdown
from ollama_evals.runner import CaseResult, RunResult


def _run(run_id, rows):
    results = [CaseResult(m, cid, cat, s, s == 1.0) for (m, cid, cat, s) in rows]
    manifest = {"run_id": run_id, "models": sorted({r[0] for r in rows})}
    return RunResult(manifest=manifest, results=results)


def test_run_markdown_matrix_lists_models_and_categories():
    run = _run("r", [("qwen", "c1", "coding", 1.0), ("qwen", "c2", "chat", 0.5),
                     ("llama", "c1", "coding", 0.0), ("llama", "c2", "chat", 1.0)])
    md = run_to_markdown(run)
    assert "qwen" in md and "llama" in md
    assert "coding" in md and "chat" in md
    assert "Overall" in md


def test_comparison_markdown_shows_verdict_and_deltas():
    base = _run("b", [("old", "c1", "coding", 1.0)])
    cand = _run("c", [("new", "c1", "coding", 0.4)])
    reg = compare_runs(base, cand, model_baseline="old", model_candidate="new", threshold=0.1)
    md = comparison_to_markdown(reg)
    assert "REGRESSION" in md
    assert "old" in md and "new" in md
    assert "coding" in md


def test_comparison_markdown_pass_verdict():
    base = _run("b", [("old", "c1", "coding", 0.5)])
    cand = _run("c", [("new", "c1", "coding", 1.0)])
    reg = compare_runs(base, cand, model_baseline="old", model_candidate="new")
    assert "PASS" in comparison_to_markdown(reg)


def test_comparison_html_is_self_contained():
    base = _run("b", [("old", "c1", "coding", 0.5)])
    cand = _run("c", [("new", "c1", "coding", 1.0)])
    reg = compare_runs(base, cand, model_baseline="old", model_candidate="new")
    html = comparison_to_html(reg)
    assert "<html" in html.lower()
    assert "<style" in html.lower()  # inline CSS, no external stylesheet
    assert "http://" not in html and "https://" not in html  # no external resources
