"""Tests des providers OpenAI et Mistral (API chat/completions)."""

from __future__ import annotations

from unittest.mock import patch

import httpx
import pytest

from app.exceptions import InferenceError, ParseError, ProviderAPIError
from app.parsers import parse_chat_completions_response
from app.providers.mistral import MistralProvider
from app.providers.openai import OpenAIProvider
from app.services import complete

CHAT_COMPLETIONS_RESPONSE = {
    "id": "chatcmpl-test",
    "model": "gpt-4o",
    "choices": [
        {
            "index": 0,
            "message": {"role": "assistant", "content": "Salut !"},
            "finish_reason": "stop",
        }
    ],
    "usage": {
        "prompt_tokens": 8,
        "completion_tokens": 4,
        "total_tokens": 12,
    },
}

MISTRAL_RESPONSE = {
    **CHAT_COMPLETIONS_RESPONSE,
    "model": "mistral-large-latest",
    "choices": [
        {
            "index": 0,
            "message": {"role": "assistant", "content": "Bonjour Mistral !"},
            "finish_reason": "stop",
        }
    ],
}


def test_parse_chat_completions_response() -> None:
    result = parse_chat_completions_response(
        CHAT_COMPLETIONS_RESPONSE,
        model="gpt-4o",
        provider="openai",
    )
    assert result.text == "Salut !"
    assert result.model == "gpt-4o"
    assert result.usage.total_tokens == 12
    assert result.finish_reason == "stop"


def test_parse_chat_completions_response_invalid() -> None:
    with pytest.raises(ParseError):
        parse_chat_completions_response({"choices": []}, model="gpt-4o", provider="openai")


@pytest.mark.parametrize(
    ("provider_cls", "provider_id", "base_url", "model"),
    [
        (OpenAIProvider, "openai", "https://api.openai.com/v1", "gpt-4o"),
        (MistralProvider, "mistral", "https://api.mistral.ai/v1", "mistral-large-latest"),
    ],
)
def test_chat_provider_requires_base_url_and_api_key(
    provider_cls: type[OpenAIProvider],
    provider_id: str,
    base_url: str,
    model: str,
) -> None:
    provider = provider_cls({"model": model, "api_key": "sk-test"})
    with pytest.raises(InferenceError, match="base_url est obligatoire"):
        provider.complete([{"role": "user", "content": "Hi"}])

    provider = provider_cls({"model": model, "base_url": base_url})
    with pytest.raises(InferenceError, match="api_key est obligatoire"):
        provider.complete([{"role": "user", "content": "Hi"}])


@patch("app.providers.chat_completions.httpx.post")
def test_openai_provider_complete(mock_post: object) -> None:
    mock_response = httpx.Response(
        200,
        json=CHAT_COMPLETIONS_RESPONSE,
        request=httpx.Request("POST", "https://api.openai.com/v1/chat/completions"),
    )
    mock_post.return_value = mock_response

    provider = OpenAIProvider(
        {
            "model": "gpt-4o",
            "base_url": "https://api.openai.com/v1",
            "api_key": "sk-test",
            "temperature": 0.2,
            "max_tokens": 512,
        }
    )
    result = provider.complete([{"role": "user", "content": "Hello"}])

    assert result.text == "Salut !"
    mock_post.assert_called_once()
    call_kwargs = mock_post.call_args.kwargs
    assert call_kwargs["json"]["model"] == "gpt-4o"
    assert call_kwargs["headers"]["Authorization"] == "Bearer sk-test"
    assert mock_post.call_args.args[0] == "https://api.openai.com/v1/chat/completions"


@patch("app.providers.chat_completions.httpx.post")
def test_mistral_provider_complete(mock_post: object) -> None:
    mock_response = httpx.Response(
        200,
        json=MISTRAL_RESPONSE,
        request=httpx.Request("POST", "https://api.mistral.ai/v1/chat/completions"),
    )
    mock_post.return_value = mock_response

    provider = MistralProvider(
        {
            "model": "mistral-large-latest",
            "base_url": "https://api.mistral.ai/v1",
            "api_key": "mistral-test",
        }
    )
    result = provider.complete([{"role": "user", "content": "Hello"}])

    assert result.text == "Bonjour Mistral !"
    assert mock_post.call_args.args[0] == "https://api.mistral.ai/v1/chat/completions"


@patch("app.providers.chat_completions.httpx.post")
def test_openai_provider_api_error(mock_post: object) -> None:
    mock_response = httpx.Response(
        401,
        text="invalid key",
        request=httpx.Request("POST", "https://api.openai.com/v1/chat/completions"),
    )
    mock_post.return_value = mock_response

    provider = OpenAIProvider(
        {
            "model": "gpt-4o",
            "base_url": "https://api.openai.com/v1",
            "api_key": "bad",
        }
    )
    with pytest.raises(ProviderAPIError):
        provider.complete([{"role": "user", "content": "Hi"}])


@pytest.mark.django_db
@patch("app.providers.chat_completions.httpx.post")
def test_complete_service_with_openai(mock_post: object, settings: object) -> None:
    settings.INFERENCE_DEFAULT_PROVIDER = "openai"
    settings.INFERENCE_PROVIDERS = {
        "openai": {
            "backend": "app.providers.openai.OpenAIProvider",
            "model": "gpt-4o",
            "base_url": "https://api.openai.com/v1",
            "api_key": "sk-test",
        },
    }

    mock_response = httpx.Response(
        200,
        json=CHAT_COMPLETIONS_RESPONSE,
        request=httpx.Request("POST", "https://api.openai.com/v1/chat/completions"),
    )
    mock_post.return_value = mock_response

    result = complete(messages=[{"role": "user", "content": "Hello"}])
    assert result.text == "Salut !"
