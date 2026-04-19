# pyproject.toml Template — PyPI Package Scaffold

Reference for the `pypi-package-scaffold` skill. Complete `pyproject.toml` template with all required and recommended fields.

Replace `<package-name>` with the package name (lowercase, hyphens).
Replace `<Package>` with the import name (lowercase, underscores).
Replace `<Author Name>` and `<author@example.com>` with actual values.

---

## Complete pyproject.toml

```toml
[build-system]
requires = ["hatchling>=1.21.0"]
build-backend = "hatchling.build"

# --- Project Metadata ---

[project]
name = "<package-name>"
version = "0.1.0"
description = "One-line description of what this package does."
readme = "README.md"
license = {text = "MIT"}
authors = [
    {name = "<Author Name>", email = "<author@example.com>"},
]
maintainers = [
    {name = "<Author Name>", email = "<author@example.com>"},
]
keywords = ["keyword1", "keyword2"]
classifiers = [
    "Development Status :: 3 - Alpha",
    # Use "4 - Beta" or "5 - Production/Stable" when appropriate
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Programming Language :: Python :: 3 :: Only",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Typing :: Typed",
]
requires-python = ">=3.10"
dependencies = [
    # Runtime dependencies with version ranges
    # "requests>=2.28,<3",
    # "pydantic>=2.0,<3",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4",
    "pytest-cov>=4.1",
    "pytest-asyncio>=0.23",
    "mypy>=1.8",
    "ruff>=0.2",
    "hatch>=1.9",
]
docs = [
    "mkdocs>=1.5",
    "mkdocs-material>=9.5",
    "mkdocstrings[python]>=0.24",
]

[project.urls]
Homepage = "https://github.com/<owner>/<package-name>"
Repository = "https://github.com/<owner>/<package-name>"
Documentation = "https://<owner>.github.io/<package-name>"
"Bug Tracker" = "https://github.com/<owner>/<package-name>/issues"
Changelog = "https://github.com/<owner>/<package-name>/blob/main/CHANGELOG.md"

# --- Build Configuration ---

[tool.hatch.build.targets.wheel]
packages = ["src/<Package>"]

[tool.hatch.build.targets.sdist]
include = [
    "/src",
    "/tests",
    "/README.md",
    "/LICENSE",
    "/CHANGELOG.md",
]

# --- pytest ---

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = [
    "--strict-markers",
    "--strict-config",
    "-ra",
]
asyncio_mode = "auto"  # For pytest-asyncio

# --- mypy ---

[tool.mypy]
python_version = "3.10"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
no_implicit_reexport = true
strict_equality = true

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false

# --- ruff ---

[tool.ruff]
target-version = "py310"
line-length = 100
src = ["src", "tests"]

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
    "S",   # flake8-bandit (security)
    "N",   # pep8-naming
    "ANN", # flake8-annotations
]
ignore = [
    "ANN101",  # Missing type annotation for self
    "ANN102",  # Missing type annotation for cls
]

[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = ["S101", "ANN"]  # Allow assert and missing annotations in tests

# --- coverage ---

[tool.coverage.run]
source = ["src"]
branch = true

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if TYPE_CHECKING:",
    "raise NotImplementedError",
    "@abstractmethod",
]
show_missing = true
fail_under = 80  # Minimum coverage threshold
```

---

## `src/<Package>/__init__.py` Template

```python
"""
<Package> — <one-line description>.

Example usage::

    from <Package> import PublicClass

    obj = PublicClass()
    result = obj.do_something()
"""
from __future__ import annotations

from ._internal.core import PublicClass
from ._internal.utils import public_function

__all__ = [
    "PublicClass",
    "public_function",
]

__version__ = "0.1.0"
```

---

## `README.md` Template

```markdown
# <package-name>

<One-line description>

[![PyPI version](https://badge.fury.io/py/<package-name>.svg)](https://badge.fury.io/py/<package-name>)
[![Python versions](https://img.shields.io/pypi/pyversions/<package-name>.svg)](https://pypi.org/project/<package-name>/)
[![License](https://img.shields.io/pypi/l/<package-name>.svg)](https://github.com/<owner>/<package-name>/blob/main/LICENSE)
[![CI](https://github.com/<owner>/<package-name>/actions/workflows/ci.yml/badge.svg)](https://github.com/<owner>/<package-name>/actions/workflows/ci.yml)

## Installation

\`\`\`bash
pip install <package-name>
\`\`\`

## Quick Start

\`\`\`python
from <Package> import PublicClass

obj = PublicClass()
result = obj.do_something()
\`\`\`

## Documentation

Full documentation: https://<owner>.github.io/<package-name>

## License

MIT — see [LICENSE](LICENSE) for details.
```

---

## `CHANGELOG.md` Template

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release

## [0.1.0] - YYYY-MM-DD

### Added
- Initial package scaffold
- `PublicClass` with `do_something()` method
- Full type annotations
- pytest test suite
- GitHub Actions CI/CD

[Unreleased]: https://github.com/<owner>/<package-name>/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/<owner>/<package-name>/releases/tag/v0.1.0
```
