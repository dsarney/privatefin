"""Tests for Ollama availability checks and chat response handling."""

from types import SimpleNamespace

import pytest

from src.llm.ollama_client import OllamaClient


def test_is_available_returns_true_when_list_succeeds(monkeypatch):
    class FakeClient:
        def __init__(self, host):
            self.host = host

        def list(self):
            return {"models": []}

    import src.llm.ollama_client as module

    monkeypatch.setattr(module.ollama, "Client", FakeClient)

    client = OllamaClient(model="llama3", host="http://localhost:11434")
    assert client.is_available() is True


def test_is_available_returns_false_on_exception(monkeypatch):
    class FailingClient:
        def __init__(self, host):
            raise RuntimeError("unreachable")

    import src.llm.ollama_client as module

    monkeypatch.setattr(module.ollama, "Client", FailingClient)

    client = OllamaClient()
    assert client.is_available() is False


def test_generate_passes_system_and_user_messages(monkeypatch):
    captured = {}

    class FakeClient:
        def __init__(self, host):
            captured["host"] = host

        def chat(self, model, messages):
            captured["model"] = model
            captured["messages"] = messages
            return {"message": {"content": "analysis text"}}

    import src.llm.ollama_client as module

    monkeypatch.setattr(module.ollama, "Client", FakeClient)

    client = OllamaClient(model="my-model", host="http://local")
    result = client.generate("user prompt", system_prompt="system prompt")

    assert result == "analysis text"
    assert captured["model"] == "my-model"
    assert captured["messages"] == [
        {"role": "system", "content": "system prompt"},
        {"role": "user", "content": "user prompt"},
    ]


def test_generate_raises_runtime_error_on_failure(monkeypatch):
    class FailingClient:
        def __init__(self, host):
            self.host = host

        def chat(self, model, messages):
            raise RuntimeError("connection failed")

    import src.llm.ollama_client as module

    monkeypatch.setattr(module.ollama, "Client", FailingClient)

    client = OllamaClient()
    with pytest.raises(RuntimeError, match="Ollama is unavailable"):
        client.generate("user prompt")


def test_extract_content_supports_dict_and_object_styles():
    dict_response = {"message": {"content": "from dict"}}
    object_response = SimpleNamespace(message=SimpleNamespace(content="from object"))

    assert OllamaClient._extract_content(dict_response) == "from dict"
    assert OllamaClient._extract_content(object_response) == "from object"
