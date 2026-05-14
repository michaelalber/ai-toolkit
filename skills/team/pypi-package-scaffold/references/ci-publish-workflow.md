# CI/CD Publish Workflow — PyPI Package Scaffold

Reference for the `pypi-package-scaffold` skill. GitHub Actions workflows for testing and publishing Python packages using Trusted Publishing (OIDC — no API tokens required).

---

## CI Workflow (`.github/workflows/ci.yml`)

Runs on every push and pull request. Tests across Python 3.10, 3.11, 3.12, 3.13.

```yaml
name: CI

on:
  push:
    branches: ["main"]
  pull_request:
    branches: ["main"]

permissions:
  contents: read

jobs:
  test:
    name: Test Python ${{ matrix.python-version }}
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        python-version: ["3.10", "3.11", "3.12", "3.13"]

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: "pip"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[dev]"

      - name: Run tests
        run: |
          pytest tests/ -v --cov=src --cov-report=xml --cov-report=term-missing
        env:
          PYTHONHASHSEED: "0"  # Deterministic hash seed

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        if: matrix.python-version == '3.12'  # Upload once
        with:
          file: ./coverage.xml
          fail_ci_if_error: false

  lint:
    name: Lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: "pip"

      - name: Install dependencies
        run: |
          pip install ruff mypy

      - name: Run ruff
        run: ruff check src/ tests/

      - name: Run ruff format check
        run: ruff format --check src/ tests/

      - name: Run mypy
        run: mypy src/ --strict

  build:
    name: Build distribution
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install build tools
        run: pip install build twine

      - name: Build
        run: python -m build
        env:
          PYTHONHASHSEED: "0"

      - name: Check distribution
        run: twine check dist/*

      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: dist
          path: dist/
```

---

## Publish Workflow (`.github/workflows/publish.yml`)

Publishes to PyPI on tag push. Uses Trusted Publishing (OIDC) — no API tokens needed.

**Prerequisites:**
1. Configure Trusted Publishing on PyPI:
   - Go to PyPI → Your account → Publishing → Add a new pending publisher
   - Set: Owner = `<owner>`, Repository = `<package-name>`, Workflow = `publish.yml`, Environment = `pypi`
2. Create a GitHub environment named `pypi` with required reviewers (optional but recommended)

```yaml
name: Publish to PyPI

on:
  push:
    tags:
      - "v*"  # Trigger on version tags: v1.0.0, v1.2.3, etc.

permissions:
  contents: read
  id-token: write  # Required for Trusted Publishing (OIDC)

jobs:
  test:
    name: Test before publish
    uses: ./.github/workflows/ci.yml  # Reuse CI workflow

  build:
    name: Build distribution
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install build tools
        run: pip install build twine

      - name: Build
        run: python -m build
        env:
          PYTHONHASHSEED: "0"

      - name: Check distribution
        run: twine check dist/*

      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: dist
          path: dist/

  publish-testpypi:
    name: Publish to TestPyPI
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: testpypi
      url: https://test.pypi.org/p/<package-name>
    permissions:
      id-token: write  # Required for Trusted Publishing

    steps:
      - name: Download artifacts
        uses: actions/download-artifact@v4
        with:
          name: dist
          path: dist/

      - name: Publish to TestPyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          repository-url: https://test.pypi.org/legacy/

  publish-pypi:
    name: Publish to PyPI
    needs: publish-testpypi
    runs-on: ubuntu-latest
    environment:
      name: pypi
      url: https://pypi.org/p/<package-name>
    permissions:
      id-token: write  # Required for Trusted Publishing

    steps:
      - name: Download artifacts
        uses: actions/download-artifact@v4
        with:
          name: dist
          path: dist/

      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        # No username/password needed — Trusted Publishing uses OIDC
```

---

## Release Checklist

Before creating a release tag:

```markdown
## Release Checklist: v[X.Y.Z]

### Code Quality
- [ ] All tests pass: `pytest tests/ -v`
- [ ] Type check passes: `mypy src/ --strict`
- [ ] Lint passes: `ruff check src/ tests/`
- [ ] Coverage ≥ 80%: `pytest --cov=src --cov-report=term-missing`

### Documentation
- [ ] CHANGELOG.md updated with all changes since last release
- [ ] README.md reflects current API
- [ ] Docstrings updated for changed functions/classes
- [ ] Version in `pyproject.toml` updated

### Build Verification
- [ ] `python -m build` succeeds
- [ ] `twine check dist/*` passes
- [ ] Wheel installs correctly in a fresh venv

### Release
- [ ] Create git tag: `git tag v[X.Y.Z]`
- [ ] Push tag: `git push origin v[X.Y.Z]`
- [ ] Verify GitHub Actions publish workflow succeeds
- [ ] Verify TestPyPI package installs: `pip install --index-url https://test.pypi.org/simple/ <package-name>==X.Y.Z`
- [ ] Verify PyPI package installs: `pip install <package-name>==X.Y.Z`
- [ ] Create GitHub Release with CHANGELOG section
```

---

## Trusted Publishing Setup (PyPI)

Trusted Publishing eliminates the need for API tokens. Setup steps:

1. Log in to PyPI (https://pypi.org)
2. Go to your account settings → Publishing
3. Click "Add a new pending publisher"
4. Fill in:
   - **PyPI project name:** `<package-name>`
   - **Owner:** `<github-username-or-org>`
   - **Repository name:** `<package-name>`
   - **Workflow name:** `publish.yml`
   - **Environment name:** `pypi` (must match the environment in the workflow)
5. Click "Add"

The first publish will claim the package name on PyPI. Subsequent publishes use the same Trusted Publisher configuration.

**TestPyPI setup:** Repeat the same steps on https://test.pypi.org with environment name `testpypi`.
