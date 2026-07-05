import httpx
import pytest

from ollama_evals.client import OllamaClient


def _mock_client(handler) -> httpx.Client:
    return httpx.Client(transport=httpx.MockTransport(handler))


def test_chat_posts_to_completions_endpoint_and_parses_content():
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        import json

        captured["url"] = str(request.url)
        captured["body"] = json.loads(request.content)
        return httpx.Response(
            200,
            json={
                "model": "qwen2.5-coder:7b",
                "choices": [{"message": {"role": "assistant", "content": "42"}}],
            },
        )

    client = OllamaClient("http://host:11434/v1", http_client=_mock_client(handler))
    result = client.chat(
        model="qwen2.5-coder:7b",
        messages=[{"role": "user", "content": "2+2*20?"}],
        temperature=0.0,
        seed=7,
        num_ctx=8192,
    )

    assert captured["url"] == "http://host:11434/v1/chat/completions"
    assert captured["body"]["model"] == "qwen2.5-coder:7b"
    assert captured["body"]["temperature"] == 0.0
    assert captured["body"]["seed"] == 7
    assert captured["body"]["options"]["num_ctx"] == 8192
    assert result.content == "42"
    assert result.model == "qwen2.5-coder:7b"


def test_chat_parses_tool_calls():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "model": "llama3.1:8b",
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": None,
                            "tool_calls": [
                                {
                                    "id": "call_1",
                                    "type": "function",
                                    "function": {
                                        "name": "get_weather",
                                        "arguments": '{"city": "Paris"}',
                                    },
                                }
                            ],
                        }
                    }
                ],
            },
        )

    client = OllamaClient("http://host:11434/v1", http_client=_mock_client(handler))
    result = client.chat(model="llama3.1:8b", messages=[{"role": "user", "content": "weather?"}])

    assert result.content == ""
    assert len(result.tool_calls) == 1
    assert result.tool_calls[0]["name"] == "get_weather"
    assert result.tool_calls[0]["arguments"] == {"city": "Paris"}


def test_list_models_hits_native_tags_endpoint_not_v1():
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        return httpx.Response(
            200,
            json={"models": [{"name": "qwen2.5-coder:7b"}, {"name": "llama3.1:8b"}]},
        )

    client = OllamaClient("http://host:11434/v1", http_client=_mock_client(handler))
    models = client.list_models()

    assert captured["url"] == "http://host:11434/api/tags"
    assert models == ["qwen2.5-coder:7b", "llama3.1:8b"]


def test_chat_passes_tools_and_max_tokens():
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        import json

        captured["body"] = json.loads(request.content)
        return httpx.Response(200, json={"choices": [{"message": {"content": "ok"}}]})

    client = OllamaClient("http://host:11434/v1", http_client=_mock_client(handler))
    tools = [{"type": "function", "function": {"name": "f", "parameters": {}}}]
    client.chat(model="x", messages=[{"role": "user", "content": "hi"}], tools=tools, max_tokens=64)

    assert captured["body"]["tools"] == tools
    assert captured["body"]["max_tokens"] == 64


def test_tool_call_with_invalid_json_arguments_keeps_raw_string():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": None,
                            "tool_calls": [
                                {"function": {"name": "f", "arguments": "{not json"}}
                            ],
                        }
                    }
                ]
            },
        )

    client = OllamaClient("http://host:11434/v1", http_client=_mock_client(handler))
    result = client.chat(model="x", messages=[{"role": "user", "content": "hi"}])
    assert result.tool_calls[0]["arguments"] == "{not json"


def test_chat_raises_on_http_error():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, json={"error": "boom"})

    client = OllamaClient("http://host:11434/v1", http_client=_mock_client(handler))
    with pytest.raises(httpx.HTTPStatusError):
        client.chat(model="x", messages=[{"role": "user", "content": "hi"}])
