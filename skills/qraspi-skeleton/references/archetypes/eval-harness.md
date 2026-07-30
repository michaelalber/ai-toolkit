# Archetype: Eval harness / AI tooling project (Python, infrastructure-heavy)

A new project whose product IS an evaluation/AI-tooling pipeline. The brief says the Skeleton includes
"eval harness scaffolding where applicable." Here fitness functions and evals overlap conceptually --
both are executable acceptance gates -- so the boundary needs naming explicitly.

## Stack it instantiates (from the ADRs)
Python 3.10+, the ADR-chosen LLM/embedding stack (Ollama / cloud API), a vector store if RAG, pytest
+ an eval runner. Confirm against the accepted ADRs.

## Repo layer (the recipe)
- Layout: `src/<pkg>/{pipeline,evals}/`, `datasets/`, `tests/`, `pyproject.toml`, an `evals.md` (seed
  from `project-templates/evals.md`) declaring acceptance criteria BEFORE the pipeline grows.
- Entrypoint: one input -> pipeline stage(s) -> output -> one scored eval, end-to-end (the walking
  slice), doing minimal real work.
- Health/smoke: a pytest that runs the one-input pipeline and asserts the eval produces a score.
- Observability hook: structured run logging; if the ADRs use LangSmith-style tracing, wire one trace.
- Secure-by-default: API keys via env only; bind any local server to `127.0.0.1`; no prompt secrets
  in source -- prompt templates live in versioned files, never f-strings.

## Slice layer (delegate)
Invoke `rag-pipeline-python` (or `mcp-server-scaffold` if the tool is MCP-exposed; both in the edge-ai-robotics-automation-toolkit supplement) for the one
pipeline slice. Keep prompts in versioned template files per the AI/ML coding standards.

## evals vs fitness functions (name the boundary)
- **Evals** verify the *output is good* relative to intent (quality of the answer). They live in
  `evals/` and gate on a score threshold.
- **Fitness functions** verify the *structure is legal* (layering, coverage, dependency policy).
- Both are CI gates here. Wire both via `fitness-functions`; keep the eval-score gate separate from
  the architectural gates so a regression points to the right cause.

## CI-green command
`.github/workflows/ci.yml` running `ruff check . && mypy src && pytest --cov && python -m evals.run
--threshold` -> exit 0. No hardware gate. `ci_green` is the captured exit status.
