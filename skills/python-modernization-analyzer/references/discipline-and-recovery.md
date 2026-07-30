# AI Discipline, Anti-Patterns & Error Recovery — Python Modernization

Reference for the `python-modernization-analyzer` skill. Discipline rules to follow, anti-patterns
to avoid, and recovery procedures for common assessment failures.

---

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

---

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

---

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
