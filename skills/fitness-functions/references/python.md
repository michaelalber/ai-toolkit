# Fitness Functions — Python (import-linter)

Tool: **import-linter** — declares import contracts (layered, forbidden, independence) and checks
them with the `lint-imports` CLI, which exits non-zero on violation. It reads the real import graph,
not a hand-maintained list. For coupling *metrics*, defer to `dependency-mapper`.

## 1. Minimal check

Enforce a layered architecture ADR — higher layers may import lower, never the reverse:

```ini
# .importlinter  (or [tool.importlinter] in pyproject.toml)
[importlinter]
root_package = myapp

# Gates ADR-0004: api -> services -> domain, one direction only.
[importlinter:contract:layers]
name = Layered architecture
type = layers
layers =
    myapp.api
    myapp.services
    myapp.domain
```

Install: `pip install import-linter` (pin it in `pyproject.toml` dev deps).

## 2. CI wiring (GitHub Actions)

```yaml
# .github/workflows/ci.yml
  - name: Import contracts (gates ADR-0004)
    run: lint-imports --config .importlinter
```

`lint-imports` prints each broken contract and the offending import chain, then exits 1 → the job
fails → branch protection blocks merge.

## 3. Prove it gates

1. Run `lint-imports` → must report "Contracts: 1 kept, 0 broken" today.
2. Add a deliberate violation: in `myapp/domain/` import from `myapp.services`. Re-run → must
   report the contract broken with the illegal import chain.
3. Revert. Commit only the green state.

## Other ready-made Python fitness functions

- **Coverage threshold:** `pytest --cov=myapp --cov-fail-under=80` fails the build under target.
- **Forbidden-module contract:** `type = forbidden` to ban e.g. `myapp.domain` importing `requests`
  (keep I/O out of the domain).
- **Dependency policy / CVEs:** `pip-audit` as a separate gate (supply-chain fitness function).
