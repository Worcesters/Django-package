"""Base partagée pour les APIs OpenAI-compatible (/v1/chat/completions)."""

from __future__ import annotations

from typing import Any

import httpx

from inference.exceptions import (
    InferenceError,
    ProviderAPIError,
    ProviderConnectionError,
    RateLimitError,
)
from inference.parsers import parse_chat_completions_response
from inference.providers.base import BaseLLMProvider
from inference.schemas import CompletionResult

CHAT_ENDPOINT = "/chat/completions"


class ChatCompletionsProvider(BaseLLMProvider):
    """Provider HTTP pour les APIs type OpenAI (OpenAI, Mistral, ...)."""

    def complete(self, messages: list[dict[str, str]]) -> CompletionResult:
        base_url = self._resolve_base_url()
        api_key = self._resolve_api_key()
        model = str(self.config["model"])
        timeout = float(self.config.get("timeout", 60))

        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": float(self.config.get("temperature", 0.7)),
            "max_tokens": int(self.config.get("max_tokens", 1024)),
        }
        extra = self.config.get("extra") or {}
        if isinstance(extra, dict):
            payload.update(extra)

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        try:
            response = httpx.post(
                f"{base_url}{CHAT_ENDPOINT}",
                json=payload,
                headers=headers,
                timeout=timeout,
            )
        except (httpx.TimeoutException, httpx.ConnectError, httpx.NetworkError) as exc:
            raise ProviderConnectionError(
                f"Connexion {self.provider_id} impossible ({base_url}).",
                provider=self.provider_id,
            ) from exc

        if response.status_code == 429:
            raise RateLimitError(
                f"{self.provider_id} a renvoyé une limite de débit (429).",
                provider=self.provider_id,
            )

        if response.status_code >= 400:
            raise ProviderAPIError(
                f"{self.provider_id} HTTP {response.status_code} : {response.text[:200]}",
                provider=self.provider_id,
            )

        return parse_chat_completions_response(
            response.json(),
            model=model,
            provider=self.provider_id,
        )

    def _resolve_base_url(self) -> str:
        base_url = self.config.get("base_url")
        if not base_url:
            raise InferenceError(
                f"base_url est obligatoire pour le provider {self.provider_id}. "
                f"Définissez INFERENCE_PROVIDERS['{self.provider_id}']['base_url'] dans les settings.",
                provider=self.provider_id,
                code="missing_base_url",
            )
        return str(base_url).rstrip("/")

    def _resolve_api_key(self) -> str:
        api_key = self.config.get("api_key")
        if not api_key:
            raise InferenceError(
                f"api_key est obligatoire pour le provider {self.provider_id}. "
                f"Définissez api_key ou api_key_env dans INFERENCE_PROVIDERS.",
                provider=self.provider_id,
                code="missing_api_key",
            )
        return str(api_key)
