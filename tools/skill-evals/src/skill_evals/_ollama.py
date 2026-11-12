# <AI-Generated START>
"""The single import seam onto ollama-evals.

Exactly one module knows the LLM layers depend on a sibling package. L1 must stay runnable
with only typer/pyyaml/rich — it is the layer anyone runs daily — so the dependency is an
optional extra and this shim turns a missing install into one clear sentence rather than a
traceback from six call sites.
"""

from __future__ import annotations

_MISSING = (
    "the LLM layers need ollama-evals. Install it with:\n"
    "    uv sync --extra llm\n"
    "or, with pip:\n"
    "    pip install -e ../ollama-evals && pip install -e '.[llm]'"
)


class OllamaEvalsMissing(RuntimeError):
    pass


class EndpointError(RuntimeError):
    """The model server is unreachable, or refused the request (bad model name, etc.)."""


def describe_endpoint_error(exc: Exception, base_url: str, model: str | None = None) -> str:
    """Turn an httpx failure into something a human can act on.

    A raw traceback out of the HTTP client reads as a bug in the harness. Almost always it
    is a wrong model name or an endpoint that is not up, and saying so is the whole job.
    """
    status = getattr(getattr(exc, "response", None), "status_code", None)
    if status == 404:
        return (
            f"{base_url} returned 404 for model {model!r}. That model is probably not "
            "pulled on this server — check `ollama-evals list-models`."
        )
    if status is not None:
        return f"{base_url} returned HTTP {status}: {exc}"
    return f"could not reach {base_url}: {exc}"


def endpoint_errors() -> tuple[type[Exception], ...]:
    """The exception types an endpoint call can raise, without importing httpx eagerly."""
    try:
        import httpx
    except ImportError:  # pragma: no cover - httpx ships with ollama-evals
        return (OSError,)
    return (httpx.HTTPError, OSError)


def is_endpoint_error(result) -> bool:
    """ollama-evals' run_suite catches per-case exceptions and records them this way —
    score 0 with ``detail="error: ..."``. That is a failed request, not a model answer."""
    return (getattr(result, "detail", "") or "").startswith("error:")


class RecordingClient:
    """Passes calls through; keeps the first transport failure for a useful error message.

    run_suite swallows per-case exceptions, so without this a wrong model name never
    reaches the caller and a run of 404s reads as a run of bad answers.
    """

    def __init__(self, inner):
        self._inner = inner
        self.first_error: Exception | None = None
        self.first_error_model: str | None = None

    def chat(self, *args, **kwargs):
        try:
            return self._inner.chat(*args, **kwargs)
        except endpoint_errors() as exc:
            if self.first_error is None:
                self.first_error = exc
                # Model under test or judge — whichever request actually failed.
                self.first_error_model = kwargs.get("model", args[0] if args else None)
            raise

    def __getattr__(self, name):
        return getattr(self._inner, name)


def require():
    """Import the ollama-evals surface skill-evals uses, or explain how to get it."""
    try:
        from ollama_evals import cases, client, compare, config, judging, report, runner
        from ollama_evals.scorers import base as scorers_base
    except ImportError as exc:  # pragma: no cover - exercised by the message test
        raise OllamaEvalsMissing(_MISSING) from exc

    return {
        "cases": cases,
        "client": client,
        "compare": compare,
        "config": config,
        "judging": judging,
        "report": report,
        "runner": runner,
        "scorers_base": scorers_base,
    }


def available() -> bool:
    try:
        require()
    except OllamaEvalsMissing:
        return False
    return True
# <AI-Generated END>
