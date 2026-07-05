# <AI-Generated START>
"""Thin client for an Ollama server's OpenAI-compatible API.

Talks to ``{base_url}/chat/completions`` for generation and to the native
``{root}/api/tags`` endpoint (which lives outside ``/v1``) for model discovery.
An ``httpx.Client`` can be injected for testing.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field

import httpx

DEFAULT_TIMEOUT = 120.0


@dataclass
class ChatResult:
    model: str
    content: str
    tool_calls: list[dict] = field(default_factory=list)
    raw: dict = field(default_factory=dict)


class OllamaClient:
    def __init__(
        self,
        base_url: str,
        http_client: httpx.Client | None = None,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self._client = http_client or httpx.Client(timeout=timeout)

    def _tags_url(self) -> str:
        # /api/tags is the native Ollama endpoint and is NOT under /v1.
        root = self.base_url
        if root.endswith("/v1"):
            root = root[: -len("/v1")]
        return f"{root}/api/tags"

    def chat(
        self,
        model: str,
        messages: list[dict],
        temperature: float = 0.0,
        seed: int | None = None,
        num_ctx: int | None = None,
        tools: list[dict] | None = None,
        max_tokens: int | None = None,
    ) -> ChatResult:
        payload: dict = {"model": model, "messages": messages, "temperature": temperature}
        if seed is not None:
            payload["seed"] = seed
        if num_ctx is not None:
            # Ollama-specific context size; passed via options passthrough.
            payload["options"] = {"num_ctx": num_ctx}
        if tools:
            payload["tools"] = tools
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens

        resp = self._client.post(f"{self.base_url}/chat/completions", json=payload)
        resp.raise_for_status()
        data = resp.json()
        message = (data.get("choices") or [{}])[0].get("message") or {}
        return ChatResult(
            model=data.get("model", model),
            content=message.get("content") or "",
            tool_calls=_parse_tool_calls(message.get("tool_calls")),
            raw=data,
        )

    def list_models(self) -> list[str]:
        resp = self._client.get(self._tags_url())
        resp.raise_for_status()
        return [m["name"] for m in resp.json().get("models", [])]


def _parse_tool_calls(tool_calls: list[dict] | None) -> list[dict]:
    parsed: list[dict] = []
    for call in tool_calls or []:
        fn = call.get("function") or {}
        args = fn.get("arguments")
        if isinstance(args, str):
            try:
                args = json.loads(args)
            except json.JSONDecodeError:
                pass  # keep the raw string if the model emitted invalid JSON
        parsed.append({"name": fn.get("name"), "arguments": args})
    return parsed
# <AI-Generated END>
