"""Embedder Ollama."""

from __future__ import annotations

from typing import Any

import httpx

from rag.embedders.base import BaseEmbedder
from rag.exceptions import EmbeddingAPIError, RagError, StoreConnectionError
from rag.schemas import EmbeddingResult

EMBED_ENDPOINT = "/api/embed"


class OllamaEmbedder(BaseEmbedder):
    embedder_id = "ollama"

    def embed(self, text: str) -> EmbeddingResult:
        return self.embed_batch([text])[0]

    def embed_batch(self, texts: list[str]) -> list[EmbeddingResult]:
        base_url = self._resolve_base_url()
        model = str(self.config["model"])
        timeout = float(self.config.get("timeout", 60))
        dimensions = int(self.config.get("dimensions", 0))

        payload: dict[str, Any] = {"model": model, "input": texts}
        extra = self.config.get("extra") or {}
        if isinstance(extra, dict):
            payload.update(extra)

        try:
            response = httpx.post(
                f"{base_url}{EMBED_ENDPOINT}",
                json=payload,
                timeout=timeout,
            )
        except (httpx.TimeoutException, httpx.ConnectError, httpx.NetworkError) as exc:
            raise StoreConnectionError(
                f"Connexion Ollama impossible ({base_url}).",
                component=self.embedder_id,
            ) from exc

        if response.status_code >= 400:
            raise EmbeddingAPIError(
                f"Ollama HTTP {response.status_code} : {response.text[:200]}",
                component=self.embedder_id,
            )

        raw = response.json()
        embeddings = raw.get("embeddings", [])
        results: list[EmbeddingResult] = []
        for vector_raw in embeddings:
            vector = [float(v) for v in vector_raw]
            results.append(
                EmbeddingResult(
                    vector=vector,
                    model=model,
                    dimensions=len(vector) or dimensions,
                    raw=raw if isinstance(raw, dict) else {},
                )
            )
        return results

    def _resolve_base_url(self) -> str:
        base_url = self.config.get("base_url")
        if not base_url:
            raise RagError(
                "base_url est obligatoire pour l'embedder ollama.",
                component=self.embedder_id,
                code="missing_base_url",
            )
        return str(base_url).rstrip("/")
