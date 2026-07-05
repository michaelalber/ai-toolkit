# <AI-Generated START>
"""Render runs and comparisons as Markdown and self-contained HTML.

HTML is deliberately dependency-free (inline CSS, no external fonts/scripts) so a report
opens anywhere and is safe to share.
"""

from __future__ import annotations

import html


def _fmt(value: float | None) -> str:
    return "—" if value is None else f"{value:.2f}"


def _fmt_delta(value: float | None) -> str:
    return "—" if value is None else f"{value:+.2f}"


def run_to_markdown(run) -> str:
    cat_means = run.category_means()
    overall = run.overall_means()
    categories = sorted({c for cats in cat_means.values() for c in cats})

    header = "| Model | " + " | ".join(categories) + " | Overall |"
    sep = "|" + "---|" * (len(categories) + 2)
    lines = [f"# Eval matrix — run `{run.manifest.get('run_id', '')}`", "", header, sep]
    for model in sorted(cat_means):
        cells = [_fmt(cat_means[model].get(c)) for c in categories]
        lines.append(f"| `{model}` | " + " | ".join(cells) + f" | **{overall[model]:.2f}** |")
    return "\n".join(lines)


def run_to_html(run) -> str:
    cat_means = run.category_means()
    overall = run.overall_means()
    categories = sorted({c for cats in cat_means.values() for c in cats})
    head_cells = "".join(f"<th>{html.escape(c)}</th>" for c in categories)
    rows = []
    for model in sorted(cat_means):
        cells = "".join(f"<td>{_fmt(cat_means[model].get(c))}</td>" for c in categories)
        rows.append(
            f"<tr><td>{html.escape(model)}</td>{cells}"
            f"<td><strong>{overall[model]:.2f}</strong></td></tr>"
        )
    run_id = html.escape(str(run.manifest.get("run_id", "")))
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>ollama-evals — matrix {run_id}</title>
<style>{_HTML_STYLE}</style></head>
<body>
<h1>Eval matrix — run {run_id}</h1>
<table>
<caption>Score by model and category (0.00–1.00)</caption>
<tr><th>Model</th>{head_cells}<th>Overall</th></tr>
{chr(10).join(rows)}
</table>
</body></html>"""


def comparison_to_markdown(reg) -> str:
    verdict = "❌ REGRESSION" if reg.regressed else "✅ PASS"
    lines = [
        f"# Regression: `{reg.model_candidate}` vs `{reg.model_baseline}`",
        "",
        f"**Verdict:** {verdict}  (gate threshold {reg.threshold:.2f})",
    ]
    if reg.regressed and reg.worst_category:
        worst = reg.categories[reg.worst_category]["delta"]
        lines.append(f"Worst category: **{reg.worst_category}** Δ{_fmt_delta(worst)}")
    lines += [
        "",
        "| Category | baseline | candidate | Δ |",
        "|---|---|---|---|",
    ]
    for cat, v in reg.categories.items():
        lines.append(
            f"| {cat} | {_fmt(v['baseline'])} | {_fmt(v['candidate'])} | {_fmt_delta(v['delta'])} |"
        )
    o = reg.overall
    lines.append(
        f"| **Overall** | {_fmt(o['baseline'])} | {_fmt(o['candidate'])} "
        f"| {_fmt_delta(o['delta'])} |"
    )
    p = reg.pairwise
    lines += ["", f"Pairwise (candidate view): {p['wins']}W / {p['losses']}L / {p['ties']}T"]
    return "\n".join(lines)


_HTML_STYLE = """
:root { color-scheme: light dark; }
body { font-family: system-ui, sans-serif; margin: 2rem auto; max-width: 60rem; padding: 0 1rem; }
table { border-collapse: collapse; width: 100%; overflow-x: auto; display: block; }
th, td { border: 1px solid #8884; padding: .4rem .6rem; text-align: right; }
th:first-child, td:first-child { text-align: left; }
.pass { color: #1a7f37; font-weight: 700; }
.fail { color: #cf222e; font-weight: 700; }
.neg { color: #cf222e; } .pos { color: #1a7f37; }
caption { text-align: left; font-weight: 700; margin-bottom: .5rem; }
"""


def comparison_to_html(reg) -> str:
    verdict_class = "fail" if reg.regressed else "pass"
    verdict_text = "❌ REGRESSION" if reg.regressed else "✅ PASS"
    rows = []
    for cat, v in reg.categories.items():
        rows.append(_html_row(cat, v["baseline"], v["candidate"], v["delta"]))
    o = reg.overall
    rows.append(_html_row("Overall", o["baseline"], o["candidate"], o["delta"], strong=True))
    p = reg.pairwise
    title = f"{reg.model_candidate} vs {reg.model_baseline}"
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>ollama-evals — {html.escape(title)}</title>
<style>{_HTML_STYLE}</style></head>
<body>
<h1>Regression: {html.escape(reg.model_candidate)} vs {html.escape(reg.model_baseline)}</h1>
<p>Verdict: <span class="{verdict_class}">{verdict_text}</span>
 &nbsp;(gate threshold {reg.threshold:.2f})</p>
<table>
<caption>Per-category scores</caption>
<tr><th>Category</th><th>baseline</th><th>candidate</th><th>&Delta;</th></tr>
{chr(10).join(rows)}
</table>
<p>Pairwise (candidate view): {p['wins']}W / {p['losses']}L / {p['ties']}T</p>
</body></html>"""


def _html_row(label, baseline, candidate, delta, strong=False):
    delta_cls = "" if delta is None else ("neg" if delta < 0 else "pos")
    safe = html.escape(str(label))
    label_html = f"<strong>{safe}</strong>" if strong else safe
    return (
        f"<tr><td>{label_html}</td><td>{_fmt(baseline)}</td>"
        f"<td>{_fmt(candidate)}</td><td class=\"{delta_cls}\">{_fmt_delta(delta)}</td></tr>"
    )
# <AI-Generated END>
