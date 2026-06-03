# Archetype: Python MCP server (small, single-service, library-heavy)

A new FastMCP server exposing tools to an AI assistant. Small surface -- the Architecture phase
likely produced only 1-2 ADRs (transport, tool-surface shape). QRASPI must **scale down** here: a
six-phase ceremony on a single-service library must not out-weigh the system. Keep the skeleton thin.

## Stack it instantiates (from the ADRs)
Python 3.10+, FastMCP, pytest, `pyproject.toml`. Confirm against the accepted ADRs -- never assume.

## Repo layer (the recipe)
- Layout: `src/<pkg>/server.py` (FastMCP app), `src/<pkg>/tools/`, `tests/`, `pyproject.toml`.
- Entrypoint: a FastMCP server exposing ONE trivial tool end-to-end (the walking slice).
- Health/smoke: a pytest that starts the server in-process and calls the one tool, asserting a real
  round-trip response.
- Observability hook: structured logging on tool invocation (stdout; the MCP host captures it).
- Secure-by-default: bind to stdio or `127.0.0.1` only; no secrets in source; inputs validated with
  Pydantic v2 at the tool boundary.

## Slice layer (delegate)
Invoke `mcp-server-scaffold` for the one tool the skeleton walks. Do not scaffold the full tool
surface -- one tool, end-to-end.

## Fitness gates typical here (wire via `fitness-functions`)
Light, matching the small surface: `ruff` lint gate, `mypy` type gate, `pip-audit` dependency gate,
coverage threshold on the one slice. The global `ruff` PostToolUse hook is the local precedent; the CI
gate is its merge-blocking analog.

## CI-green command
`.github/workflows/ci.yml` running `ruff check . && mypy src && pytest --cov` -> exit 0. No hardware
gate. `ci_green` is the captured exit status of that run.
