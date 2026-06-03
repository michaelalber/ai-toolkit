# PyPI Package Output Template

The scaffold progress checklist the skill reports to the user.

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
