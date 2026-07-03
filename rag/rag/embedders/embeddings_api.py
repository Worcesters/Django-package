"""Base partagée pour les APIs OpenAI-compatible (/v1/embeddings)."""

from __future__ import annotations

from typing import Any

import httpx

from rag.embedders.base import BaseEmbedder
from rag.exceptions import EmbedderConnectionError, EmbeddingAPIError, RagError
from rag.schemas import EmbeddingResult

EMBED_ENDPOINT = "/embeddings"


class OpenAICompatibleEmbedder(BaseEmbedder):
    """Embedder HTTP pour les APIs type OpenAI (OpenAI, Mistral, ...)."""

    def embed(self, text: str) -> EmbeddingResult:
        return self.embed_batch([text])[0]

    def embed_batch(self, texts: list[str]) -> list[EmbeddingResult]:
        base_url = self._resolve_base_url()
        api_key = self._resolve_api_key()
        model = str(self.config["model"])
        timeout = float(self.config.get("timeout", 60))
        dimensions = int(self.config.get("dimensions", 0))

        payload: dict[str, Any] = {"model": model, "input": texts}
        extra = self.config.get("extra") or {}
        if isinstance(extra, dict):
            payload.update(extra)

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        try:
            response = httpx.post(
                f"{base_url}{EMBED_ENDPOINT}",
                json=payload,
                headers=headers,
                timeout=timeout,
            )
        except (httpx.TimeoutException, httpx.ConnectError, httpx.NetworkError) as exc:
            raise EmbedderConnectionError(
                f"Connexion {self.embedder_id} impossible ({base_url}).",
                component=self.embedder_id,
            ) from exc

        if response.status_code >= 400:
            raise EmbeddingAPIError(
                f"{self.embedder_id} HTTP {response.status_code} : {response.text[:200]}",
                component=self.embedder_id,
            )

        return _parse_embeddings_response(
            response.json(),
            model=model,
            expected_dimensions=dimensions,
        )

    def _resolve_base_url(self) -> str:
        base_url = self.config.get("base_url")
        if not base_url:
            raise RagError(
                f"base_url est obligatoire pour l'embedder {self.embedder_id}.",
                component=self.embedder_id,
                code="missing_base_url",
            )
        return str(base_url).rstrip("/")

    def _resolve_api_key(self) -> str:
        api_key = self.config.get("api_key")
        if not api_key:
            raise RagError(
                f"api_key est obligatoire pour l'embedder {self.embedder_id}.",
                component=self.embedder_id,
                code="missing_api_key",
            )
        return str(api_key)


def _parse_embeddings_response(
    raw: dict[str, Any],
    *,
    model: str,
    expected_dimensions: int,
) -> list[EmbeddingResult]:
    data = raw.get("data", [])
    usage = raw.get("usage", {})
    results: list[EmbeddingResult] = []
    for item in sorted(data, key=lambda entry: int(entry.get("index", 0))):
        vector = [float(v) for v in item.get("embedding", [])]
        results.append(
            EmbeddingResult(
                vector=vector,
                model=model,
                dimensions=len(vector) or expected_dimensions,
                usage=dict(usage) if isinstance(usage, dict) else {},
                raw=item if isinstance(item, dict) else {},
            )
        )
    return results
