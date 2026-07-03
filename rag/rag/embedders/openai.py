"""Embedder OpenAI."""

from __future__ import annotations

from rag.embedders.embeddings_api import OpenAICompatibleEmbedder


class OpenAIEmbedder(OpenAICompatibleEmbedder):
    embedder_id = "openai"
