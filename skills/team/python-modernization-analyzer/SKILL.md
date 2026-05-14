---
name: python-modernization-analyzer
description: Analyzes legacy Python codebases and produces actionable modernization plans. Primary migration paths include Python 2 to 3.12+, sync to async, Flask/Django monolith to FastAPI, requirements.txt to pyproject.toml, and bare classes to Pydantic/dataclasses. Does NOT perform the migration — assesses, quantifies risk, and plans. Triggers on phrases like "modernize python", "python 2 to 3", "upgrade python", "migrate flask to fastapi", "python legacy migration", "async migration python", "python modernization", "upgrade python codebase", "python technical debt".
---

# Python Modernization Analyzer

> "The best time to modernize was five years ago. The second best time is now."
> -- Adapted from software engineering practice

> "Big bang rewrites fail. Incremental migration succeeds."
> -- Martin Fowler, *Refactoring*

## Core Philosophy

Legacy Python codebases accumulate technical debt in predictable patterns: Python 2 syntax that `2to3` can partially fix, synchronous I/O that blocks under load, monolithic Flask/Django apps that resist scaling, `requirements.txt` files with unpinned dependencies, and bare dictionaries where Pydantic models would provide safety.

This skill assesses, quantifies, and plans — it does NOT perform the migration. The output is a prioritized modernization plan with risk scores, effort estimates, and a recommended migration sequence. The plan is the deliverable; execution is a separate task.

**Non-Negotiable Constraints:**
1. **Assess before acting** — never recommend a migration path without evidence from the codebase
2. **Incremental over big-bang** — every recommendation must be achievable in phases, not a single rewrite
3. **Preserve business logic unchanged** — the goal is modernization, not reimplementation
4. **Dependencies are the real blockers** — a framework migration blocked by an unmaintained dependency is not viable
5. **Every recommendation must cite evidence** — "I think this is Flask" is not evidence; `grep -r "from flask"` is

**What this skill is NOT:**
- It is NOT a migration execution tool — it produces a plan, not code
- It is NOT a code quality review — use `python-arch-review` for that
- It is NOT a security review — use `python-security-review` for that

## Domain Principles

| # | Principle | Description | Applied As |
|---|-----------|-------------|------------|
| 1 | **Risk Assessment First** | Every modernization recommendation carries risk. Quantify it before recommending it. A Python 2→3 migration on a 50,000-line codebase with no tests is a different risk than the same migration on a 5,000-line codebase with 80% coverage. | Score every migration path: Effort (S/M/L/XL), Risk (Low/Med/High/Critical), Blocker potential |
| 2 | **Incremental Migration** | Big-bang rewrites fail. Every migration path must be decomposable into phases that each leave the application in a working state. If a migration cannot be done incrementally, it is too risky to recommend without a detailed plan. | Every recommendation includes a phased approach with intermediate checkpoints |
| 3 | **API Compatibility Analysis** | Before recommending a framework migration, verify that the new framework can serve the same API surface. A Flask app with custom middleware may not map cleanly to FastAPI. | Run `pyupgrade --py312-plus` in dry-run mode; use `2to3 -l` to list required changes |
| 4 | **Dependency Audit** | The migration is only as viable as its dependencies. An unmaintained package that only supports Python 2 blocks the entire migration. Identify blockers before recommending a timeline. | Run `pip-audit`, `pip list --outdated`, and check PyPI for Python 3 compatibility |
| 5 | **Business Logic Isolation** | Before migrating, identify where business logic lives. If it is scattered across views, models, and utility functions, the migration will be harder. Recommend isolating business logic as a prerequisite step. | Map business logic locations; recommend service layer extraction before framework migration |
| 6 | **Test Coverage Gate** | Characterization tests (tests that document current behavior without asserting correctness) must exist before migrating. Without tests, you cannot verify the migration preserved behavior. | Assess current test coverage; recommend characterization test creation as Phase 0 |
| 7 | **Configuration Migration** | `requirements.txt` with unpinned dependencies is a security and reproducibility risk. `pyproject.toml` with pinned versions is the modern standard. This is usually the lowest-risk, highest-value migration. | Always recommend `requirements.txt` → `pyproject.toml` as an early, low-risk win |
| 8 | **Authentication and Identity** | Authentication migrations (Flask-Login → FastAPI JWT, Django auth → custom) are high-risk because they affect every user. Recommend these last, after the framework migration is stable. | Flag auth migrations as high-risk; recommend a parallel auth system during transition |
| 9 | **Database Access Layer** | Raw SQL → SQLAlchemy ORM and sync SQLAlchemy → async SQLAlchemy are separate migrations. Never combine them. | Assess ORM usage; recommend separate phases for ORM adoption and async migration |
| 10 | **Deployment Pipeline** | Bare scripts and manual deployments are a modernization blocker. Recommend Docker + CI/CD as infrastructure prerequisites before framework migrations. | Assess deployment maturity; flag missing CI/CD as a prerequisite |

## Knowledge Base Lookups

Use `search_knowledge` (grounded-code-mcp) to ground decisions in authoritative references.

| Query | When to Call |
|-------|--------------|
| `search_knowledge("python 2 to 3 migration 2to3 pyupgrade")` | At SCAN phase — confirm Python 2→3 migration tooling |
| `search_knowledge("Flask to FastAPI migration async")` | When assessing framework migration paths |
| `search_knowledge("SQLAlchemy sync to async migration")` | When assessing async migration paths |
| `search_knowledge("pyproject.toml packaging pip dependency management")` | When assessing packaging modernization |
| `search_knowledge("python characterization tests legacy code")` | When recommending test coverage as a prerequisite |

## Workflow

### Phase 1: SCAN

**Objective:** Inventory the codebase to understand its current state.

**Steps:**

1. Identify Python version(s) in use
2. Identify framework(s): Flask, Django, FastAPI, bare WSGI/ASGI, or none
3. Identify packaging: `requirements.txt`, `setup.py`, `setup.cfg`, or `pyproject.toml`
4. Identify test framework and coverage level
5. Identify async usage (or absence)
6. Identify ORM/database access pattern
7. Identify deployment method

```bash
# Python version
python --version
find . -name "*.py" | xargs grep -l "print " | head -5  # Python 2 print statements
find . -name "*.py" | xargs grep -l "unicode\|basestring\|xrange" | head -5  # Python 2 builtins

# Framework detection
grep -r "from flask\|import flask" --include="*.py" | head -5
grep -r "from django\|import django" --include="*.py" | head -5
grep -r "from fastapi\|import fastapi" --include="*.py" | head -5

# Packaging
ls requirements*.txt setup.py setup.cfg pyproject.toml 2>/dev/null

# Test coverage
find . -name "test_*.py" -o -name "*_test.py" | wc -l
grep -r "import pytest\|import unittest" --include="*.py" | wc -l

# Async usage
grep -r "async def\|await\|asyncio" --include="*.py" | wc -l

# Python 2 compatibility tools
2to3 -l .  # List required changes (dry run)
pyupgrade --py312-plus --dry-run $(find . -name "*.py") 2>&1 | head -30
```

### Phase 2: ASSESS

**Objective:** Score each migration path by effort, risk, and blocker potential.

**Migration paths to assess:**

| Path | Tool | Assessment Method |
|------|------|------------------|
| Python 2 → 3.12+ | `2to3`, `pyupgrade` | Run in dry-run mode; count required changes |
| Sync → async | Manual analysis | Count blocking I/O calls; assess framework support |
| Flask/Django → FastAPI | Manual analysis | Map routes, middleware, auth; check dependency compatibility |
| `requirements.txt` → `pyproject.toml` | `pip-audit`, `pip list --outdated` | Count unpinned deps; check for Python 3 compatibility |
| Bare classes → Pydantic | Manual analysis | Count dict-based data structures; assess validation gaps |
| Raw SQL → SQLAlchemy | Manual analysis | Count raw SQL queries; assess query complexity |

Use `references/migration-risk-matrix.md` for scoring guidance.

### Phase 3: PLAN

**Objective:** Produce a prioritized, phased modernization plan.

**Plan structure:**
1. **Phase 0: Prerequisites** — tests, CI/CD, Docker (if missing)
2. **Phase 1: Low-risk wins** — packaging, type hints, linting
3. **Phase 2: Framework-independent** — Python version upgrade, dependency updates
4. **Phase 3: Architecture** — service layer extraction, ORM adoption
5. **Phase 4: Framework** — Flask/Django → FastAPI (if applicable)
6. **Phase 5: Async** — sync → async migration (if applicable)
7. **Phase 6: Auth** — authentication modernization (last, highest risk)

### Phase 4: REPORT

**Objective:** Deliver the modernization plan with evidence, risk scores, and effort estimates.

Use `references/migration-risk-matrix.md` for the risk scoring table.

## State Block

```xml
<python-modernization-state>
  phase: SCAN | ASSESS | PLAN | REPORT | COMPLETE
  python_version: [2.x / 3.x / unknown]
  framework: flask | django | fastapi | bare | unknown
  packaging: requirements_txt | setup_py | pyproject_toml | unknown
  test_coverage: none | low | medium | high | unknown
  async_usage: none | partial | full
  migration_paths_identified: 0
  blockers_identified: 0
  last_action: [description]
  next_action: [description]
</python-modernization-state>
```

## Output Templates

### Modernization Assessment Summary

```markdown
## Python Modernization Assessment: [Application Name]

**Date:** YYYY-MM-DD
**Python Version:** [current]
**Framework:** [Flask / Django / FastAPI / None]
**Codebase Size:** [lines of code, file count]
**Test Coverage:** [%]

### Migration Paths Identified

| Path | Effort | Risk | Blockers | Recommended Order |
|------|--------|------|---------|------------------|
| requirements.txt → pyproject.toml | S | Low | None | 1 (immediate) |
| Python 3.9 → 3.12 | M | Low | [dep X not 3.12 compatible] | 2 |
| Add type hints | L | Low | None | 3 |
| Flask → FastAPI | XL | High | [dep Y Flask-only] | 5 (after service layer) |
| Sync → async | XL | High | [SQLAlchemy sync] | 6 (after FastAPI) |

### Blockers

| Blocker | Affected Path | Resolution |
|---------|--------------|-----------|
| [package X] v1.2 — Python 2 only | Python 2→3 | Fork or replace with [alternative] |
| [package Y] — Flask-only | Flask→FastAPI | No FastAPI equivalent; manual port required |

### Recommended Phased Plan

**Phase 0 (Prerequisites — 1-2 weeks):**
- [ ] Add pytest and achieve ≥ 60% coverage on critical paths
- [ ] Add Docker + CI/CD pipeline

**Phase 1 (Low-risk wins — 1 week):**
- [ ] Migrate requirements.txt → pyproject.toml
- [ ] Add ruff linting to CI
- [ ] Run pyupgrade --py312-plus

[Continue for each phase...]
```

## AI Discipline Rules

### CRITICAL: Evidence Before Recommendation

**WRONG:**
```
This looks like a Flask application. I recommend migrating to FastAPI.
```

**RIGHT:**
```
Framework detection:
  grep -r "from flask" --include="*.py" → 47 matches across 12 files
  grep -r "from fastapi" --include="*.py" → 0 matches

This is a Flask application. FastAPI migration is a viable path.
Blockers to assess: [list dependencies that may not support FastAPI]
```

### REQUIRED: Quantify Before Scoring

**WRONG:** "The Python 2→3 migration is high risk."

**RIGHT:** "The Python 2→3 migration requires changes in 234 files (2to3 dry-run output). 3 dependencies have no Python 3 equivalent. Test coverage is 12%. Risk: High."

### CRITICAL: Incremental Plans Only

**WRONG:** "Rewrite the application in FastAPI."

**RIGHT:** "Phase 1: Extract service layer from Flask views (2 weeks). Phase 2: Add FastAPI alongside Flask (1 week). Phase 3: Migrate routes one by one (4 weeks). Phase 4: Remove Flask (1 week)."

## Anti-Patterns Table

| # | Anti-Pattern | Why It Fails | Correct Approach |
|---|-------------|-------------|-----------------|
| 1 | **Big-bang rewrite recommendation** | Rewrites fail; business logic is lost; timeline explodes | Recommend incremental migration with working checkpoints |
| 2 | **Recommending migration without test coverage** | Cannot verify behavior is preserved | Recommend characterization tests as Phase 0 |
| 3 | **Ignoring dependency blockers** | A blocked dependency makes the migration impossible | Audit all dependencies for compatibility before recommending a path |
| 4 | **Combining multiple migrations** | Flask→FastAPI + sync→async + Python 2→3 simultaneously is unmanageable | Sequence migrations; one major change at a time |
| 5 | **Recommending auth migration early** | Auth affects every user; failure is catastrophic | Auth migration is always last, after the framework is stable |
| 6 | **No effort estimates** | A plan without estimates cannot be scheduled | Every phase must have an effort estimate (S/M/L/XL or days) |
| 7 | **Assessing without running tools** | `2to3` and `pyupgrade` dry-run output is evidence; intuition is not | Always run assessment tools before scoring |
| 8 | **Recommending async migration without ORM assessment** | Async SQLAlchemy requires different session management than sync | Assess ORM before recommending async migration |
| 9 | **Skipping deployment assessment** | A modernized app that cannot be deployed is not modernized | Assess CI/CD and Docker maturity as prerequisites |
| 10 | **Treating all codebases the same** | A 500-line script and a 500,000-line monolith require different approaches | Scale recommendations to codebase size and team capacity |

## Error Recovery

### `2to3` or `pyupgrade` not installed

```
Symptoms: Assessment tools not available

Recovery:
1. Install: pip install 2to3 pyupgrade
2. If not installable in the current environment: run in a separate venv
3. If the codebase is Python 2 only: install Python 2 first, then 2to3
4. Document the tool versions used in the assessment report
```

### Dependency compatibility cannot be determined

```
Symptoms: A key dependency has no clear Python 3 / FastAPI compatibility information

Recovery:
1. Check PyPI for the package: does it have Python 3 classifiers?
2. Check the package's GitHub/GitLab for recent activity and open issues
3. Check if there is a maintained fork
4. If no information: mark as "Unknown — manual investigation required" in the blockers table
5. Do not assume compatibility without evidence
```

### Test coverage is zero

```
Symptoms: No test files found; coverage cannot be measured

Recovery:
1. Document: "Test coverage: 0% — no test files found"
2. Add to Phase 0: "Create characterization tests for critical paths before any migration"
3. Recommend: pytest + pytest-cov; target 60% coverage on critical paths before Phase 1
4. Do not recommend any migration until Phase 0 is complete
5. Flag this as the highest-risk factor in the assessment
```

## Integration with Other Skills

| Skill | Relationship |
|-------|-------------|
| `python-arch-review` | Run architecture review after modernization to verify the new structure meets quality gates. |
| `python-security-review` | Run security review after framework migration — new frameworks have different security patterns. |
| `alembic-migration-manager` | Database migration is often part of modernization. Use this skill for the migration lifecycle. |
| `fastapi-scaffolder` | When the modernization plan includes FastAPI adoption, use this skill for endpoint scaffolding. |
| `legacy-migration-analyzer` | Cross-reference for teams with mixed Python/.NET stacks. Assessment philosophy is identical; tooling differs. |
