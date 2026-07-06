"""Tests for the Ollama client boundary (httpx mocked)."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import httpx
import pytest

from code2md.enrich.ollama_client import OllamaClient, OllamaError


def _resp(json_body: dict) -> MagicMock:
    m = MagicMock()
    m.raise_for_status.return_value = None
    m.json.return_value = json_body
    return m


class TestGenerate:
    @patch("code2md.enrich.ollama_client.httpx.post")
    def test_returns_response_text(self, post: MagicMock) -> None:
        post.return_value = _resp({"response": '{"summary":"ok"}'})
        out = OllamaClient("http://host:11434").generate("m", "prompt")
        assert out == '{"summary":"ok"}'
        # json_format adds the format=json constraint
        assert post.call_args.kwargs["json"]["format"] == "json"

    @patch("code2md.enrich.ollama_client.httpx.post")
    def test_http_error_becomes_ollama_error(self, post: MagicMock) -> None:
        post.side_effect = httpx.ConnectError("refused")
        with pytest.raises(OllamaError):
            OllamaClient("http://host:11434").generate("m", "p")

    @patch("code2md.enrich.ollama_client.httpx.post")
    def test_empty_response_raises(self, post: MagicMock) -> None:
        post.return_value = _resp({"response": "   "})
        with pytest.raises(OllamaError):
            OllamaClient("http://host:11434").generate("m", "p")

    @patch("code2md.enrich.ollama_client.httpx.post")
    def test_no_json_format_when_disabled(self, post: MagicMock) -> None:
        post.return_value = _resp({"response": "text"})
        OllamaClient("http://host:11434").generate("m", "p", json_format=False)
        assert "format" not in post.call_args.kwargs["json"]
