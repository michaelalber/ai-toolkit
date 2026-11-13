# python-architecture-checklist — operating guide

Depth relocated from SKILL.md; load it when the Workflow points here.

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

Tooling config: [ruff](references/ruff-config.md) · [mypy](references/mypy-config.md). Full section-by-section list + grounding query map: [review checklist](references/review-checklist.md).

## AI Discipline Rules

- **Detect the Python version first.** Recommending `match` statements or `tomllib` to a 3.9 project produces invalid findings.
- **Evidence or it is not a finding.** Run the tools; cite `file:line`. Never grade on vibes.
- **Architecture, not security.** Vulnerability findings (injection, deserialization, secrets exposure) belong to `python-security-review` — note them and route there.
- **Do not rewrite during a review.** Produce findings + recommendations; the team decides and `tdd-loop` drives the fix.
