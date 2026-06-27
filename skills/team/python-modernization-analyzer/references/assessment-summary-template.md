# Assessment Summary Template — Python Modernization

Reference for the `python-modernization-analyzer` skill. The Phase 4 (REPORT) deliverable.
Compatibility before/after examples are in `compatibility-patterns.md`; risk scoring is in
`migration-risk-matrix.md`.

---

## Modernization Assessment Summary

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
