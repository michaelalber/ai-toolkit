---
name: python-architecture-checklist
audience: team
description: >
  Grades an existing Python codebase. Detects Python version, framework (FastAPI/Django/Flask),
  and package layout, then checks clean-architecture boundaries, type-safety discipline,
  complexity, dependency direction, and config/secrets hygiene with file:line evidence. Use to
  review or grade a Python codebase. Not for Socratic critique (architecture-review), security
  audits (python-security-review), or new test-first code (tdd).
---

# Python Architecture Checklist

> "A checklist cannot fly a plane, but a pilot cannot fly safely without one."
> — Atul Gawande

## Core Philosophy

Shared across the `dotnet` / `python` / `php` / `rust` architecture checklists — same values, language-specific checks.

| # | Value | What it means |
|---|-------|---------------|
| 1 | **Detect before judge** | Determine version/framework/structure before applying any item; context decides what is idiomatic. |
| 2 | **Evidence over opinion** | Every finding cites `file:line` and the offending pattern. "Overuses globals" is not a finding; "`config.py:12` mutates a module-level global" is. |
| 3 | **Feature cohesion** | Organized by business capability, not technical layer. Cross-feature coupling is a violation. |
| 4 | **Dependencies point inward** | Domain logic does not import infrastructure (DB, HTTP, filesystem). Boundaries are explicit. |
| 5 | **Explicit error handling** | Failures handled at the right layer; no silent swallowing; errors carry diagnostic context. |
| 6 | **Config & secrets hygiene** | No hardcoded secrets; configuration injected, not reached for globally; secrets from env / secret-manager. |
| 7 | **Version awareness** | Recommendations are gated to the detected version; never suggest an API that does not exist there. |
| 8 | **Tests gate change** | Untested code is a finding; high-risk modules without tests are prioritized. |
| 9 | **Graded, actionable output** | A letter grade (A–F) from counted findings, plus prioritized, version-correct recommendations. |

## Workflow

Shared skeleton: `DETECT → SCAN → REPORT → RECOMMEND`.

```
DETECT     Python version (pyproject.toml / .python-version), framework (FastAPI/Django/Flask),
           layout (src/ vs flat, packages), and whether a test suite exists. Record findings; if a
           version cannot be determined, ask — never assume 3.13.

SCAN       Run the Python Checklist below section by section. Gather evidence with tooling:
             ruff check .         # style + lint + complexity drift
             mypy <pkg>           # type completeness and correctness
             radon cc -s <pkg>    # cyclomatic complexity hot spots
             radon mi <pkg>       # maintainability index
           Every violation becomes a finding with file:line and a severity (critical/high/medium/low).

REPORT     Emit the graded report (Output Template). Grade = function of counted findings.

RECOMMEND  Prioritize: critical → quick wins → modernization. Version-gate every recommendation;
           never suggest an API absent from the detected Python version.
```

## Python Checklist (language-specific)

| # | Check | Severity |
|---|-------|----------|
| 1 | **Clean boundaries** — domain modules import zero infrastructure; boundaries use `typing.Protocol`; no circular imports | Critical |
| 2 | **Type safety** — all public functions fully annotated; `mypy` clean; no bare `# type: ignore` (each needs a reason) | High |
| 3 | **YAGNI / Rule of Three** — abstractions justified by ≥3 concrete uses; no speculative base classes or plugin layers | High |
| 4 | **Complexity** — `radon cc` grade ≥ B per function; maintainability index ≥ 70; no god-modules | High |
| 5 | **Dependency discipline** — versions pinned in `pyproject.toml` (not `setup.py`); stdlib preferred; each dep justified | Medium |
| 6 | **Async discipline** — `async def` for I/O-bound work; no blocking calls (`time.sleep`, sync I/O) inside `async`; `ProcessPoolExecutor` for CPU-bound | High |
| 7 | **Resource lifecycle** — file handles / sessions / connections via context managers, not manual open/close | Medium |
| 8 | **Config & secrets** — settings via `pydantic` `BaseSettings`; secrets from env; no hardcoded credentials | Critical |
| 9 | **Test coverage** — behavioral tests exist for business logic; AAA; high-risk untested modules flagged | High |

Tooling config: [ruff](references/ruff-config.md) · [mypy](references/mypy-config.md). Full section-by-section list: [review checklist](references/review-checklist.md).

## State Block

```
<arch-checklist-state>
language: python
mode: DETECT | SCAN | REPORT | RECOMMEND | COMPLETE
detected: [python 3.x | framework | layout | tests:yes/no]
issues_found: [critical:N high:N medium:N low:N]
last_action: [what was just done]
next_action: [what should happen next]
</arch-checklist-state>
```

## Output Template

Shared across all four architecture checklists.

```markdown
## Architecture Checklist: [project] (Python)
**Version**: [3.x] | **Framework**: [FastAPI/Django/Flask/none] | **Tests**: [yes/no]

| Section | Pass | Fail | Warn |
|---------|------|------|------|
| Boundaries / Types / Complexity / Deps / Async / Config / Tests | … | … | … |

### Grade: [A–F]
Grading: **A** 0 crit/0 high/≤3 med · **B** 0 crit/≤2 high · **C** 0 crit, gaps in one area ·
**D** 1+ crit · **F** fundamental problems (no boundaries, secrets in code, untyped public API).

| Severity | Location | Finding | Recommendation |
|----------|----------|---------|----------------|
| CRITICAL | file:line | [pattern] | [version-gated fix] |

**Quick wins**: [low-effort, high-impact] · **Modernization**: [larger items with effort estimate]
```

## AI Discipline Rules

- **Detect the Python version first.** Recommending `match` statements or `tomllib` to a 3.9 project produces invalid findings.
- **Evidence or it is not a finding.** Run the tools; cite `file:line`. Never grade on vibes.
- **Architecture, not security.** Vulnerability findings (injection, deserialization, secrets exposure) belong to `python-security-review` — note them and route there.
- **Do not rewrite during a review.** Produce findings + recommendations; the team decides and `tdd` drives the fix.

## Integration with Other Skills

- **`architecture-review`** — When the grade is D/F, escalate to the Socratic critic: this checklist finds _what_ is wrong; `architecture-review` builds _why_.
- **`python-security-review`** — Companion for the security dimension (OWASP, bandit, pip-audit).
- **`python-feature-slice`** — Correct-pattern reference when the checklist flags structural violations.
- **`tdd`** — Methodology for adding tests the checklist flags as missing, and for driving any refactor.
- **`dotnet` / `php` / `rust`-architecture-checklist** — Sibling skills sharing this exact Core Values + workflow + output.
