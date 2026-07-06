"""Minimal Ollama client for build-time enrichment.

Wraps the local ``/api/generate`` endpoint. This is the seam tests mock, so the
summarizer never needs a live model.
"""
from __future__ import annotations

import httpx


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
            "options": {"temperature": 0.2},
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
