"""Minimal Ollama client for build-time enrichment.

Wraps the local ``/api/generate`` endpoint. This is the seam tests mock, so the
summarizer never needs a live model.
"""
from __future__ import annotations

import httpx

# Context-window sizing. Ollama defaults to a ~4k-token window, which silently
# truncates whole-file enrichment prompts (a 24 KB source file is ~8k tokens) and
# makes the model return an empty or partial response. Size num_ctx to the prompt
# instead: a comfortable floor for short calls, growing to fit large files, capped
# to bound KV-cache memory on the host.
_CTX_FLOOR = 8192
_CTX_CAP = 32768
_CTX_STEP = 4096
_OUTPUT_HEADROOM_TOKENS = 2048
# Conservative chars-per-token for code (denser than prose) so we round context up,
# never under, the true token count.
_CHARS_PER_TOKEN = 3


def estimate_num_ctx(prompt: str) -> int:
    """Pick a num_ctx that fits ``prompt`` plus output headroom, within bounds."""
    needed = len(prompt) // _CHARS_PER_TOKEN + _OUTPUT_HEADROOM_TOKENS
    rounded = ((needed + _CTX_STEP - 1) // _CTX_STEP) * _CTX_STEP
    return max(_CTX_FLOOR, min(_CTX_CAP, rounded))


class OllamaError(RuntimeError):
    """Raised when the Ollama endpoint fails or returns an unusable response."""


class OllamaClient:
    def __init__(self, host: str, timeout_s: float = 180.0) -> None:
        self._host = host.rstrip("/")
        self._timeout_s = timeout_s

    def generate(self, model: str, prompt: str, *, json_format: bool = True) -> str:
        """Return the model's completion text for ``prompt``.

        With ``json_format`` the request asks Ollama to constrain output to JSON;
        the caller is still responsible for parsing (and tolerating) it.
        """
        payload: dict[str, object] = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.2, "num_ctx": estimate_num_ctx(prompt)},
        }
        if json_format:
            payload["format"] = "json"

        try:
            response = httpx.post(
                f"{self._host}/api/generate", json=payload, timeout=self._timeout_s
            )
            response.raise_for_status()
            data = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise OllamaError(f"Ollama request failed: {exc}") from exc

        text = data.get("response")
        if not isinstance(text, str) or not text.strip():
            raise OllamaError("Ollama returned an empty response")
        return text
