# PyPI Package Conventions

Depth behind the Core Philosophy constraints: principles, knowledge-base grounding, anti-patterns,
discipline rules, and recovery. The complete `pyproject.toml` is in `pyproject-template.md`; the
GitHub Actions publish workflow in `ci-publish-workflow.md`.

## Domain Principles

| # | Principle | Description | Applied As |
|---|-----------|-------------|------------|
| 1 | **Semantic Versioning** | `MAJOR.MINOR.PATCH`; breaking→MAJOR, feature→MINOR, fix→PATCH; pre-release `1.0.0a1/b1/rc1` | Version in `pyproject.toml`; git tag; enforced in CI |
| 2 | **API Surface Minimization** | Export only what users need; `__all__` defines the public API; internal modules use `_` prefix | `__all__ = [...]` in `src/<package>/__init__.py` |
| 3 | **Python Version Support** | Current stable + two previous minors | `requires-python = ">=3.10"`; CI matrix covers all |
| 4 | **Documentation** | Docstrings on all public APIs; README with install/quickstart/API; mkdocs or sphinx for full docs | Google/NumPy-style docstrings; README.md at root |
| 5 | **Deterministic Builds** | Pinned build deps; `PYTHONHASHSEED=0` in CI; reproducible `python -m build` | `[build-system] requires = ["hatchling==1.x.x"]` |
| 6 | **Type Stubs** | Ship `py.typed` (PEP 561); inline types preferred; `mypy --strict` passes | `src/<package>/py.typed` (empty); mypy in CI |
| 7 | **License Compliance** | SPDX identifier; `LICENSE` at root; compatible with all deps | `license = {text = "MIT"}` or `{file = "LICENSE"}` |
| 8 | **Dependency Management** | Libraries use ranges with upper bounds; applications pin exact | `dependencies = ["requests>=2.28,<3"]` |
| 9 | **Backward Compatibility** | Deprecation warnings before removal; ≥ 1 minor version between deprecate and remove | `warnings.warn(..., DeprecationWarning, stacklevel=2)` |
| 10 | **Source Distribution + Wheel** | Always ship sdist + wheel; pure-Python ships universal wheels | `python -m build`; verify with `twine check dist/*` |

## Knowledge Base Lookups

| Query | When to Call |
|-------|--------------|
| `search_knowledge("pyproject.toml package metadata hatch flit build")` | SCAFFOLD — pyproject structure |
| `search_knowledge("semantic versioning python package PyPI")` | Configuring versioning |
| `search_knowledge("GitHub Actions python publish PyPI workflow")` | Configuring CI/CD |
| `search_knowledge("python type stubs py.typed inline types")` | Configuring type stubs |
| `search_knowledge("python package src layout test structure")` | Project structure |

## Command Sequences

```bash
# TEST
pip install -e ".[dev]"
pytest tests/ -v --cov=src/<package> --cov-report=term-missing
mypy src/<package> --strict
ruff check src/ tests/ && ruff format --check src/ tests/

# BUILD
python -m build
twine check dist/*
python -m zipfile -l dist/<package>-*.whl

# PUBLISH (TestPyPI first, then PyPI)
twine upload --repository testpypi dist/*
pip install --index-url https://test.pypi.org/simple/ <package>
twine upload dist/*
```

## Required Metadata Checklist

`name`, `version` (SemVer), `description`, `readme`, `license` (SPDX), `authors` ({name, email}),
`requires-python`, `classifiers` (trove), `dependencies` (with version ranges),
`[project.urls]` (Homepage, Repository, Documentation, Bug Tracker).

## Discipline Rules

- **No publish without tests.** The `publish` job must declare `needs: test`; never `twine upload`
  in a workflow that didn't run the full test matrix first.
- **`__all__` defines the public API.** Export only intended names from `__init__.py`; internal
  classes and `_private` helpers must not be re-exported.
- **Version ranges for library dependencies.** `"requests>=2.28,<3"`, never `">=2.28"` — an unbounded
  range breaks when the dependency's next major releases.

## Anti-Patterns

| # | Anti-Pattern | Why It Fails | Correct Approach |
|---|-------------|-------------|-----------------|
| 1 | Publishing without tests | Broken packages reach users; trust is lost | `needs: test` in publish workflow |
| 2 | No `__all__` | Internal implementation leaks into the public API | Define `__all__` in every `__init__.py` |
| 3 | Flat layout (no `src/`) | Tests import the source tree, masking packaging bugs | Use `src/<package>/` layout |
| 4 | Unpinned build dependencies | Build output changes when tools update | Pin `hatchling`/`flit`/`build` versions |
| 5 | No upper bound on dependencies | Dependency breaking changes break the package silently | `>=X.Y,<Z` for all library deps |
| 6 | No `py.typed` marker | Type checkers can't use the package's inline types | Add empty `py.typed` to the package root |
| 7 | No CHANGELOG | Users can't tell what changed between versions | Maintain `CHANGELOG.md` with SemVer sections |
| 8 | PyPI before TestPyPI | PyPI mistakes can't be deleted (only yanked) | Always publish to TestPyPI first |
| 9 | API tokens in CI | Tokens can be stolen; rotation is manual | Use Trusted Publishing (OIDC) — no tokens |
| 10 | No `twine check` | Malformed distributions fail to install silently | Always `twine check dist/*` before publishing |

## Error Recovery

**`twine check` fails:**
1. Read the error — it usually names the issue
2. Common: invalid README RST/Markdown (fix formatting); missing metadata (add to pyproject); description too long (trim)
3. Re-run `python -m build`, then `twine check dist/*`; never publish until it passes

**Package installs but imports fail** (`ModuleNotFoundError` after `pip install` succeeds):
1. Is `__init__.py` in the right place? Check `[tool.hatch.build.targets.wheel]` or equivalent
2. Inspect wheel contents: `python -m zipfile -l dist/*.whl`; check for missing subpackage `__init__.py`
3. Confirm in a fresh venv: `pip install dist/*.whl`

**GitHub Actions publish fails (403 / invalid token):**
1. API tokens: verify the token is in GitHub Secrets
2. Trusted Publishing: configure the publisher on PyPI (owner, repo, workflow filename, environment)
3. Verify the workflow triggers on tag push and the environment name matches between PyPI and the workflow
