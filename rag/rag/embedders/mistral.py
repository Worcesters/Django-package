"""Embedder Mistral."""

from __future__ import annotations

from rag.embedders.embeddings_api import OpenAICompatibleEmbedder


class MistralEmbedder(OpenAICompatibleEmbedder):
    embedder_id = "mistral"
