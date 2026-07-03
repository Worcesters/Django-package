"""Tests du provider Ollama."""

from __future__ import annotations

from unittest.mock import patch

import httpx
import pytest

from completion.exceptions import InferenceError, ParseError, ProviderAPIError, ProviderConnectionError
from completion.parsers import parse_ollama_response
from completion.providers.ollama import OllamaProvider
from completion.services import complete


OLLAMA_RESPONSE = {
    "model": "llama3.2",
    "message": {"role": "assistant", "content": "Bonjour !"},
    "done": True,
    "prompt_eval_count": 10,
    "eval_count": 5,
}


def test_parse_ollama_response() -> None:
    result = parse_ollama_response(OLLAMA_RESPONSE, model="llama3.2")
    assert result.text == "Bonjour !"
    assert result.model == "llama3.2"
    assert result.usage.prompt_tokens == 10
    assert result.usage.completion_tokens == 5
    assert result.usage.total_tokens == 15
    assert result.finish_reason == "stop"


def test_parse_ollama_response_invalid() -> None:
    with pytest.raises(ParseError):
        parse_ollama_response({"done": True}, model="llama3.2")


def test_ollama_provider_requires_base_url() -> None:
    provider = OllamaProvider({"model": "llama3.2"})
    with pytest.raises(InferenceError, match="base_url est obligatoire"):
        provider.complete([{"role": "user", "content": "Bonjour"}])


@patch("completion.providers.ollama.httpx.post")
def test_ollama_provider_complete(mock_post: object) -> None:
    mock_response = httpx.Response(
        200,
        json=OLLAMA_RESPONSE,
        request=httpx.Request("POST", "http://localhost:11434/api/chat"),
    )
    mock_post.return_value = mock_response

    provider = OllamaProvider(
        {
            "model": "llama3.2",
            "base_url": "http://localhost:11434",
            "temperature": 0.5,
            "max_tokens": 256,
            "timeout": 30,
        }
    )
    result = provider.complete([{"role": "user", "content": "Bonjour"}])

    assert result.text == "Bonjour !"
    mock_post.assert_called_once()
    call_kwargs = mock_post.call_args.kwargs
    assert call_kwargs["json"]["model"] == "llama3.2"
    assert call_kwargs["json"]["stream"] is False
    assert call_kwargs["json"]["options"]["temperature"] == 0.5
    assert call_kwargs["json"]["options"]["num_predict"] == 256


@patch("completion.providers.ollama.httpx.post")
def test_ollama_provider_connection_error(mock_post: object) -> None:
    mock_post.side_effect = httpx.ConnectError("refused")

    provider = OllamaProvider({"model": "llama3.2", "base_url": "http://localhost:11434"})
    with pytest.raises(ProviderConnectionError):
        provider.complete([{"role": "user", "content": "Hi"}])


@patch("completion.providers.ollama.httpx.post")
def test_ollama_provider_api_error(mock_post: object) -> None:
    mock_response = httpx.Response(
        500,
        text="internal error",
        request=httpx.Request("POST", "http://localhost:11434/api/chat"),
    )
    mock_post.return_value = mock_response

    provider = OllamaProvider({"model": "llama3.2", "base_url": "http://localhost:11434"})
    with pytest.raises(ProviderAPIError):
        provider.complete([{"role": "user", "content": "Hi"}])


@pytest.mark.django_db
@patch("completion.providers.ollama.httpx.post")
def test_complete_service_with_llama(mock_post: object, settings: object) -> None:
    settings.INFERENCE_DEFAULT_PROVIDER = "llama"
    settings.INFERENCE_PROVIDERS = {
        "llama": {
            "backend": "completion.providers.ollama.OllamaProvider",
            "model": "llama3.2",
            "base_url": "http://localhost:11434",
        },
    }

    mock_response = httpx.Response(
        200,
        json=OLLAMA_RESPONSE,
        request=httpx.Request("POST", "http://localhost:11434/api/chat"),
    )
    mock_post.return_value = mock_response

    result = complete(messages=[{"role": "user", "content": "Bonjour"}])
    assert result.text == "Bonjour !"
