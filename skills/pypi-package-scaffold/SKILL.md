---
name: pypi-package-scaffold
description: Scaffolds production-ready PyPI packages with pyproject.toml, hatch/flit/build tooling, GitHub Actions publish workflow, test harness, and documentation. Python analog of nuget-package-scaffold. Use when creating Python packages, setting up PyPI publishing, configuring package metadata, or building Python libraries. Triggers on phrases like "create python package", "scaffold pypi", "publish python package", "pyproject.toml setup", "python library scaffold", "python package setup", "pypi publish", "python package metadata".
---

# PyPI Package Scaffold

> "A library is only as good as its documentation and its tests."
> -- Adapted from Python packaging practice

> "Semantic versioning is a contract with your users. Break it and you break trust."
> -- Tom Preston-Werner, *Semantic Versioning 2.0.0*

## Core Philosophy

A Python package is a contract with its users. The contract has three parts: the API surface (what functions and classes are public), the version (what changes are breaking), and the metadata (who maintains it, what license it uses, what Python versions it supports).

Packaging is not an afterthought. A package that cannot be installed reliably, that has no tests, that ships without type stubs, or that has no documentation is not ready for PyPI. The scaffold must establish all of these before the first publish.

**Non-Negotiable Constraints:**
1. **No publish without tests** — `pytest` must pass before any publish workflow runs
2. **SemVer is law** — breaking changes require a major version bump; no exceptions
3. **Metadata required** — `name`, `version`, `description`, `license`, `authors`, `readme`, `requires-python`, `classifiers` are all required
4. **Multi-Python-version support** — `python_requires = ">=3.10"` minimum; test matrix covers 3.10, 3.11, 3.12, 3.13
5. **Deterministic builds** — pinned build dependencies; `PYTHONHASHSEED=0` in CI

**What this skill is NOT:**
- It is NOT a Python packaging tutorial — it assumes basic Python knowledge
- It is NOT a documentation writing guide — it provides the scaffold, not the content
- It is NOT a CI/CD guide — it provides the GitHub Actions workflow template

## Domain Principles

| # | Principle | Description | Applied As |
|---|-----------|-------------|------------|
| 1 | **Semantic Versioning** | `MAJOR.MINOR.PATCH`. Breaking changes → MAJOR. New features → MINOR. Bug fixes → PATCH. Pre-release: `1.0.0a1`, `1.0.0b1`, `1.0.0rc1`. | Version in `pyproject.toml`; tag in git; enforced in CI |
| 2 | **API Surface Minimization** | Only export what users need. `__all__` in `__init__.py` defines the public API. Internal modules use `_` prefix. | `__all__ = ["PublicClass", "public_function"]` in `src/<package>/__init__.py` |
| 3 | **Python Version Support** | Support the current stable release and the two previous minor versions. Use `python_requires = ">=3.10"`. Test matrix covers all supported versions. | `python_requires = ">=3.10"` in `pyproject.toml`; matrix in CI |
| 4 | **Documentation** | Docstrings on all public functions and classes. README with installation, quickstart, and API reference. `mkdocs` or `sphinx` for full docs. | Google-style or NumPy-style docstrings; README.md in repo root |
| 5 | **Deterministic Builds** | Build dependencies are pinned. `PYTHONHASHSEED=0` in CI. `python -m build` produces identical output on every run. | `[build-system] requires = ["hatchling==1.x.x"]` with exact version |
| 6 | **Type Stubs** | Ship `py.typed` marker file for PEP 561 compliance. Inline types preferred over `.pyi` stubs. `mypy` passes with `strict` mode. | `src/<package>/py.typed` (empty file); `mypy --strict` in CI |
| 7 | **License Compliance** | SPDX license identifier in `pyproject.toml`. `LICENSE` file in repo root. License is compatible with all dependencies. | `license = {text = "MIT"}` or `license = {file = "LICENSE"}` |
| 8 | **Dependency Management** | Libraries use version ranges with upper bounds: `"requests>=2.28,<3"`. Applications pin exact versions. No `>=` without upper bound for libraries. | `dependencies = ["requests>=2.28,<3"]` in `pyproject.toml` |
| 9 | **Backward Compatibility** | Deprecation warnings before removal. `DeprecationWarning` in the deprecated function. Minimum one minor version between deprecation and removal. | `warnings.warn("...", DeprecationWarning, stacklevel=2)` |
| 10 | **Source Distribution + Wheel** | Always ship both `sdist` (`.tar.gz`) and `wheel` (`.whl`). Pure Python packages ship universal wheels. Extension packages ship platform-specific wheels. | `python -m build` produces both; verify with `twine check dist/*` |

## Knowledge Base Lookups

Use `search_knowledge` (grounded-code-mcp) to ground decisions in authoritative references.

| Query | When to Call |
|-------|--------------|
| `search_knowledge("pyproject.toml package metadata hatch flit build")` | At SCAFFOLD phase — confirm pyproject.toml structure |
| `search_knowledge("semantic versioning python package PyPI")` | When configuring versioning |
| `search_knowledge("GitHub Actions python publish PyPI workflow")` | When configuring CI/CD |
| `search_knowledge("python type stubs py.typed inline types")` | When configuring type stubs |
| `search_knowledge("python package src layout test structure")` | When setting up project structure |

## Workflow

### Phase 1: SCAFFOLD

**Objective:** Create the package directory structure and `pyproject.toml`.

**Project structure (src layout — recommended):**

```
<package-name>/
  src/
    <package>/
      __init__.py      # Public API + __all__
      py.typed         # PEP 561 marker (empty file)
      _internal/       # Private implementation
  tests/
    __init__.py
    test_<module>.py
  docs/
    index.md
  pyproject.toml       # All package metadata and tool config
  README.md
  LICENSE
  CHANGELOG.md
  .github/
    workflows/
      ci.yml           # Test matrix
      publish.yml      # PyPI publish on tag
```

See `references/pyproject-template.md` for complete `pyproject.toml`.

### Phase 2: CONFIGURE

**Objective:** Set up all required metadata, classifiers, and tool configuration.

**Required metadata checklist:**
- [ ] `name` — package name (lowercase, hyphens)
- [ ] `version` — SemVer string
- [ ] `description` — one-line description
- [ ] `readme` — path to README.md
- [ ] `license` — SPDX identifier
- [ ] `authors` — list of `{name, email}`
- [ ] `requires-python` — minimum Python version
- [ ] `classifiers` — PyPI trove classifiers
- [ ] `dependencies` — runtime dependencies with version ranges
- [ ] `[project.urls]` — Homepage, Repository, Documentation, Bug Tracker

### Phase 3: TEST

**Objective:** Set up pytest with coverage and run the test matrix.

```bash
# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest tests/ -v --cov=src/<package> --cov-report=term-missing

# Type check
mypy src/<package> --strict

# Lint
ruff check src/ tests/
ruff format --check src/ tests/
```

### Phase 4: BUILD

**Objective:** Build the distribution packages and verify them.

```bash
# Build sdist and wheel
python -m build

# Verify the distributions
twine check dist/*

# Check the wheel contents
python -m zipfile -l dist/<package>-*.whl
```

### Phase 5: PUBLISH

**Objective:** Publish to TestPyPI first, then PyPI.

```bash
# Publish to TestPyPI (test first)
twine upload --repository testpypi dist/*

# Verify installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ <package>

# Publish to PyPI (production)
twine upload dist/*
```

See `references/ci-publish-workflow.md` for the automated GitHub Actions workflow.

## State Block

```xml
<pypi-package-state>
  phase: SCAFFOLD | CONFIGURE | TEST | BUILD | PUBLISH | COMPLETE
  package_name: [name]
  version: [semver]
  python_requires: [version]
  build_tool: hatchling | flit | setuptools | build
  type_stubs: true | false
  ci_configured: true | false
  testpypi_published: true | false
  pypi_published: true | false
  last_action: [description]
  next_action: [description]
</pypi-package-state>
```

## Output Templates

### Package Scaffold Checklist

```markdown
## PyPI Package Scaffold: [package-name]

### pyproject.toml
- [ ] `name` set
- [ ] `version` set (SemVer)
- [ ] `description` set (one line)
- [ ] `readme` set
- [ ] `license` set (SPDX)
- [ ] `authors` set
- [ ] `requires-python` set
- [ ] `classifiers` set
- [ ] `dependencies` set with version ranges
- [ ] `[project.urls]` set

### Project Structure
- [ ] `src/<package>/__init__.py` with `__all__`
- [ ] `src/<package>/py.typed` (empty file)
- [ ] `tests/` directory with test files
- [ ] `README.md`
- [ ] `LICENSE`
- [ ] `CHANGELOG.md`

### Quality Gates
- [ ] `pytest` passes
- [ ] `mypy --strict` passes
- [ ] `ruff check` passes
- [ ] `twine check dist/*` passes

### CI/CD
- [ ] `ci.yml` — test matrix (Python 3.10, 3.11, 3.12, 3.13)
- [ ] `publish.yml` — publish on tag (Trusted Publishing)
```

## AI Discipline Rules

### CRITICAL: No Publish Without Tests

**WRONG:**
```yaml
# publish.yml
on:
  push:
    tags: ["v*"]
jobs:
  publish:
    steps:
      - uses: actions/checkout@v4
      - run: python -m build
      - run: twine upload dist/*  # No tests!
```

**RIGHT:**
```yaml
jobs:
  test:
    # Run full test matrix first
  publish:
    needs: test  # Publish only if tests pass
    steps:
      - run: python -m build
      - run: twine upload dist/*
```

### REQUIRED: `__all__` Defines the Public API

**WRONG:**
```python
# __init__.py — no __all__
from ._internal.core import InternalClass, PublicClass
from ._internal.utils import _private_helper, public_helper
# Users can import InternalClass and _private_helper — not intended
```

**RIGHT:**
```python
# __init__.py
from ._internal.core import PublicClass
from ._internal.utils import public_helper

__all__ = ["PublicClass", "public_helper"]
# InternalClass and _private_helper are not exported
```

### CRITICAL: Version Ranges for Library Dependencies

**WRONG:**
```toml
dependencies = ["requests>=2.28"]  # No upper bound — breaks when requests 3.0 releases
```

**RIGHT:**
```toml
dependencies = ["requests>=2.28,<3"]  # Upper bound prevents unexpected breaking changes
```

## Anti-Patterns Table

| # | Anti-Pattern | Why It Fails | Correct Approach |
|---|-------------|-------------|-----------------|
| 1 | **Publishing without tests** | Broken packages reach users; trust is lost | `needs: test` in publish workflow |
| 2 | **No `__all__`** | Internal implementation leaks into public API | Define `__all__` in every `__init__.py` |
| 3 | **Flat layout (no `src/`)** | Tests can import from the source tree, not the installed package — masks packaging bugs | Use `src/<package>/` layout |
| 4 | **Unpinned build dependencies** | Build output changes when build tools update | Pin `hatchling`, `flit`, or `build` versions |
| 5 | **No upper bound on dependencies** | Breaking changes in dependencies break the package silently | Use `>=X.Y,<Z` for all library dependencies |
| 6 | **No `py.typed` marker** | Type checkers cannot use inline types from the package | Add empty `py.typed` file to package root |
| 7 | **No CHANGELOG** | Users cannot understand what changed between versions | Maintain `CHANGELOG.md` with SemVer sections |
| 8 | **Publishing to PyPI before TestPyPI** | Mistakes on PyPI cannot be deleted (only yanked) | Always publish to TestPyPI first |
| 9 | **API tokens in CI** | Tokens can be stolen; rotation is manual | Use Trusted Publishing (OIDC) — no tokens needed |
| 10 | **No `twine check`** | Malformed distributions fail to install silently | Always run `twine check dist/*` before publishing |

## Error Recovery

### `twine check` fails

```
Symptoms: twine check dist/* reports errors

Recovery:
1. Read the error message — it usually identifies the specific issue
2. Common issues:
   - README.md has invalid RST/Markdown: fix the formatting
   - Missing required metadata: add to pyproject.toml
   - Long description too long: trim README or use a shorter description
3. Re-run python -m build after fixing
4. Re-run twine check dist/* to confirm
5. Never publish until twine check passes
```

### Package installs but imports fail

```
Symptoms: pip install succeeds; import fails with ModuleNotFoundError

Recovery:
1. Check the package structure: is __init__.py in the right place?
2. Check pyproject.toml [tool.hatch.build.targets.wheel] or equivalent
3. Verify the wheel contents: python -m zipfile -l dist/*.whl
4. Check for missing __init__.py files in subpackages
5. Install in a fresh venv to confirm: pip install dist/*.whl
```

### GitHub Actions publish fails with permission error

```
Symptoms: twine upload fails with "403 Forbidden" or "Invalid token"

Recovery:
1. If using API tokens: verify the token is set in GitHub Secrets
2. If using Trusted Publishing: verify the publisher is configured on PyPI
   - Go to PyPI → Your package → Publishing → Add a new publisher
   - Set: owner, repository, workflow filename, environment name
3. Verify the workflow is triggered by the correct event (tag push)
4. Check the environment name matches between PyPI and the workflow
```

## Integration with Other Skills

| Skill | Relationship |
|-------|-------------|
| `supply-chain-audit` | After scaffolding, audit the package's dependencies for CVEs and license compliance. |
| `python-security-review` | Review the package for security issues before publishing to PyPI. |
| `python-arch-review` | Architecture review ensures the package's internal structure is maintainable. |
| `nuget-package-scaffold` | Cross-reference for teams publishing both Python and .NET packages. Philosophy is identical; tooling differs. |
