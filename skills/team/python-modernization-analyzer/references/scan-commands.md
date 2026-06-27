# Scan & Assess Commands — Python Modernization

Reference for the `python-modernization-analyzer` skill. Detection commands for Phase 1 (SCAN)
and the migration-path catalog for Phase 2 (ASSESS).

---

## Phase 1: SCAN — Detection Commands

Inventory the codebase to understand its current state:

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

---

## Phase 2: ASSESS — Migration Path Catalog

Score each migration path by effort, risk, and blocker potential. See
`migration-risk-matrix.md` for scoring guidance and the full risk table.

| Path | Tool | Assessment Method |
|------|------|------------------|
| Python 2 → 3.12+ | `2to3`, `pyupgrade` | Run in dry-run mode; count required changes |
| Sync → async | Manual analysis | Count blocking I/O calls; assess framework support |
| Flask/Django → FastAPI | Manual analysis | Map routes, middleware, auth; check dependency compatibility |
| `requirements.txt` → `pyproject.toml` | `pip-audit`, `pip list --outdated` | Count unpinned deps; check for Python 3 compatibility |
| Bare classes → Pydantic | Manual analysis | Count dict-based data structures; assess validation gaps |
| Raw SQL → SQLAlchemy | Manual analysis | Count raw SQL queries; assess query complexity |
