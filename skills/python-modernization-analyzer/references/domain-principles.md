# Domain Principles & Knowledge Base Lookups — Python Modernization

Reference for the `python-modernization-analyzer` skill. Apply these principles throughout
all four phases. Ground each non-trivial decision with `search_knowledge`.

---

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

---

## Knowledge Base Lookups

Use `search_knowledge` (grounded-code-mcp) to ground decisions in authoritative references.

| Query | When to Call |
|-------|--------------|
| `search_knowledge("python 2 to 3 migration 2to3 pyupgrade")` | At SCAN phase — confirm Python 2→3 migration tooling |
| `search_knowledge("Flask to FastAPI migration async")` | When assessing framework migration paths |
| `search_knowledge("SQLAlchemy sync to async migration")` | When assessing async migration paths |
| `search_knowledge("pyproject.toml packaging pip dependency management")` | When assessing packaging modernization |
| `search_knowledge("python characterization tests legacy code")` | When recommending test coverage as a prerequisite |
