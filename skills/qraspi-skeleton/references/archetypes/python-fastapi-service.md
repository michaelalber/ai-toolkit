# Archetype: Python FastAPI service (web API, single service)

A new HTTP service exposing a small API. Medium weight -- the Architecture phase likely picked the
DB, the auth model, and the request/response contracts. The skeleton walks one endpoint end-to-end.

## Stack it instantiates (from the ADRs)
Python 3.10+, FastAPI, Pydantic v2, the ADR-chosen persistence (e.g. PostgreSQL via SQLAlchemy +
Alembic), pytest + httpx. Confirm against the accepted ADRs -- never assume the DB.

## Repo layer (the recipe)
- Layout: feature-based, `src/<pkg>/features/<feature>/` (router · models · service), `tests/`,
  `pyproject.toml`, Alembic dir if the ADRs use a relational DB.
- Entrypoint: one route -> Pydantic-validated request -> service -> persistence/external -> typed
  response, end-to-end (the walking slice). One route only.
- Health/smoke: a `/health` endpoint + a pytest using httpx/TestClient that exercises the one route
  against a test DB (TestContainers or SQLite).
- Observability hook: structured request logging middleware; a `/health` readiness probe.
- Secure-by-default: bind `127.0.0.1` by default; Pydantic validation at the boundary; parameterized
  queries only; secrets via env / settings, never in source.

## Slice layer (delegate)
Invoke `python-feature-slice` (FastAPI router + Pydantic v2 + service layer) for the one route. Use
`alembic-migration-manager` if the ADRs require an initial schema.

## Fitness gates typical here (wire via `fitness-functions`)
`import-linter` layer-contract gate (router never imports persistence directly), coverage threshold,
`ruff` + `mypy` gates, `pip-audit`. See `fitness-functions/references/python.md`.

## CI-green command
`.github/workflows/ci.yml` running `ruff check . && mypy src && lint-imports && pytest --cov` ->
exit 0. No hardware gate. `ci_green` is the captured exit status.
