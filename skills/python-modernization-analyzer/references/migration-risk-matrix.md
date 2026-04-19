# Migration Risk Matrix — Python Modernization

Reference for the `python-modernization-analyzer` skill. Use during Phase 2 (ASSESS) to score migration paths by effort, risk, and blocker potential.

---

## Scoring Dimensions

### Effort

| Score | Description | Typical Duration |
|-------|-------------|-----------------|
| S (Small) | Single developer, single sprint | 1-5 days |
| M (Medium) | Single developer, 2-4 sprints | 1-4 weeks |
| L (Large) | Small team, 1-3 months | 1-3 months |
| XL (Extra Large) | Team effort, 3+ months | 3+ months |

### Risk

| Score | Description | Indicators |
|-------|-------------|-----------|
| Low | Unlikely to break existing behavior; easily reversible | Tooling-assisted, no logic changes, high test coverage |
| Medium | Some behavior changes possible; reversible with effort | Partial tooling, some manual changes, medium test coverage |
| High | Significant behavior change risk; difficult to reverse | Manual migration, framework changes, low test coverage |
| Critical | High probability of breaking changes; may require rollback | No tests, complex business logic, unmaintained dependencies |

### Blocker Potential

| Score | Description |
|-------|-------------|
| None | No known blockers |
| Low | Minor blockers; workarounds available |
| Medium | Significant blockers; require investigation |
| High | Blockers may make migration infeasible |

---

## Migration Risk Scoring Table

| Migration Path | Effort | Risk | Blocker Potential | Recommended Order | Notes |
|---------------|--------|------|------------------|------------------|-------|
| `requirements.txt` → `pyproject.toml` | S | Low | None | 1 | Highest value, lowest risk |
| Add `ruff` linting | S | Low | None | 1 | No behavior change |
| Add type hints (partial) | M | Low | None | 2 | Start with public APIs |
| Python 3.9 → 3.12 | M | Low | Medium | 2 | Check dependency compatibility |
| Python 3.6/3.7 → 3.12 | L | Medium | Medium | 3 | More syntax changes; walrus operator, f-strings |
| Python 2 → 3.12 | XL | High | High | 4 | Requires `2to3`; many manual fixes |
| `setup.py` → `pyproject.toml` | M | Low | Low | 2 | More complex than requirements.txt |
| Add pytest + coverage | M | Low | None | 0 (prerequisite) | Must precede any framework migration |
| Add Docker + CI/CD | M | Low | None | 0 (prerequisite) | Must precede any framework migration |
| Raw SQL → SQLAlchemy ORM | L | Medium | Low | 3 | Preserve query semantics |
| Sync SQLAlchemy → async | L | High | Medium | 5 | Session management changes |
| Flask → FastAPI | XL | High | High | 5 | After service layer extraction |
| Django monolith → FastAPI | XL | Critical | High | 5 | Django ORM, auth, admin all change |
| Sync I/O → async | L | High | Medium | 6 | After framework migration |
| Flask-Login → FastAPI JWT | L | High | Low | 7 (last) | Auth migration is always last |
| Django auth → custom JWT | XL | Critical | Medium | 7 (last) | Affects every user |
| Bare dicts → Pydantic models | L | Low | None | 3 | No behavior change; adds validation |
| `requests` → `httpx` (async) | M | Medium | Low | 5 | With async migration |

---

## Python Version Compatibility Matrix

| Python Version | EOL Date | Key Features Added | Migration Effort from 2.7 |
|---------------|----------|-------------------|--------------------------|
| 3.8 | Oct 2024 | Walrus operator, f-string debugging | L |
| 3.9 | Oct 2025 | `dict \| dict`, `list[str]` type hints | L |
| 3.10 | Oct 2026 | Match/case, `X \| Y` union types | L |
| 3.11 | Oct 2027 | 10-60% faster, better error messages | L |
| 3.12 | Oct 2028 | f-string improvements, `@override` | L |
| 3.13 | Oct 2029 | Free-threaded mode (experimental) | L |

**Recommendation:** Target Python 3.12 for new migrations. 3.11+ provides significant performance improvements.

---

## Dependency Compatibility Assessment

For each key dependency, assess:

1. **Python 3 support:** Does the package have `Programming Language :: Python :: 3` classifiers on PyPI?
2. **Maintenance status:** Last release date; open issues; GitHub activity
3. **Alternative availability:** Is there a maintained Python 3 / async alternative?

### Common Migration Blockers

| Legacy Package | Issue | Modern Alternative |
|---------------|-------|-------------------|
| `MySQLdb` | Python 2 only | `mysqlclient` or `aiomysql` |
| `urllib2` | Python 2 only | `urllib.request` (stdlib) or `httpx` |
| `ConfigParser` | Python 2 name | `configparser` (Python 3 stdlib) |
| `cPickle` | Python 2 only | `pickle` (Python 3 stdlib) |
| `Flask-Script` | Unmaintained | Flask CLI (built-in) |
| `Flask-RESTful` | Limited async | FastAPI (if migrating) |
| `django-rest-framework` | Sync only | FastAPI + Pydantic (if migrating) |
| `celery` (old) | Check version | Celery 5.x supports Python 3.8+ |
| `SQLAlchemy` < 1.4 | No async support | SQLAlchemy 2.0 (async-first) |

---

## Effort Estimation Guidelines

### Python 2 → 3 Effort Factors

| Factor | Multiplier |
|--------|-----------|
| Lines of code | Base: 1 day per 5,000 lines |
| Test coverage < 20% | × 2.0 |
| Test coverage 20-60% | × 1.5 |
| Test coverage > 60% | × 1.0 |
| Dependency blockers (each) | + 3-5 days per blocker |
| Custom C extensions | + 5-10 days per extension |
| Complex metaclass usage | + 2-3 days |
| Heavy use of `unicode`/`str` | + 1-2 days |

### Flask → FastAPI Effort Factors

| Factor | Multiplier |
|--------|-----------|
| Number of routes | Base: 0.5 days per route |
| Custom middleware | + 2-3 days per middleware |
| Flask extensions used | + 1-2 days per extension |
| Authentication complexity | + 3-10 days |
| Test coverage < 40% | × 1.5 |
| Business logic in views | + 20-30% (service layer extraction first) |
