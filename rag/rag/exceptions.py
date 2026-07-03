"""Exceptions métier du package rag."""

from __future__ import annotations


class RagError(Exception):
    code: str = "rag_error"

    def __init__(
        self,
        message: str,
        *,
        component: str | None = None,
        code: str | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.component = component
        if code is not None:
            self.code = code


class EmbedderNotFoundError(RagError):
    code = "embedder_not_found"


class StoreNotFoundError(RagError):
    code = "store_not_found"


class EmbeddingAPIError(RagError):
    code = "embedding_api_error"


class StoreConnectionError(RagError):
    code = "store_connection_error"


class ChunkingError(RagError):
    code = "chunking_error"


class RetrievalError(RagError):
    code = "retrieval_error"


class DimensionMismatchError(RagError):
    code = "dimension_mismatch"
