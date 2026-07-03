"""Provider Ollama (Llama local et autres modèles)."""

from __future__ import annotations

from typing import Any

import httpx

from completion.exceptions import (
    InferenceError,
    ProviderAPIError,
    ProviderConnectionError,
    RateLimitError,
)
from completion.parsers import parse_ollama_response
from completion.providers.base import BaseLLMProvider
from completion.schemas import CompletionResult

CHAT_ENDPOINT = "/api/chat"


class OllamaProvider(BaseLLMProvider):
    provider_id = "llama"

    def complete(self, messages: list[dict[str, str]]) -> CompletionResult:
        """
        Envoie une requête de completion au provider Ollama.
        """

        base_url = self._resolve_base_url()
        model = str(self.config["model"])
        timeout = float(self.config.get("timeout", 60))

        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": self._build_options(),
        }

        try:
            response = httpx.post(
                f"{base_url}{CHAT_ENDPOINT}",
                json=payload,
                timeout=timeout,
            )
        except (httpx.TimeoutException, httpx.ConnectError, httpx.NetworkError) as exc:
            raise ProviderConnectionError(
                f"Connexion Ollama impossible ({base_url}).",
                provider=self.provider_id,
            ) from exc

        if response.status_code == 429:
            raise RateLimitError(
                "Ollama a renvoyé une limite de débit (429).",
                provider=self.provider_id,
            )

        if response.status_code >= 400:
            raise ProviderAPIError(
                f"Ollama HTTP {response.status_code} : {response.text[:200]}",
                provider=self.provider_id,
            )

        return parse_ollama_response(response.json(), model=model)

    def _resolve_base_url(self) -> str:
        """
        Résout l'URL de base Ollama à partir des configurations.
        """

        base_url = self.config.get("base_url")
        if not base_url:
            raise InferenceError(
                "base_url est obligatoire pour le provider llama. "
                "Définissez INFERENCE_PROVIDERS['llama']['base_url'] dans les settings.",
                provider=self.provider_id,
                code="missing_base_url",
            )
        return str(base_url).rstrip("/")

    def _build_options(self) -> dict[str, Any]:
        """
        Construit les options de la requête Ollama.
        """

        options: dict[str, Any] = {
            "temperature": float(self.config.get("temperature", 0.7)),
            "num_predict": int(self.config.get("max_tokens", 1024)),
        }
        extra = self.config.get("extra") or {}
        if isinstance(extra, dict):
            options.update(extra)
        return options
