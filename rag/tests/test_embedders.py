"""Tests des embedders rag."""

from __future__ import annotations

from unittest.mock import patch

import httpx
import pytest

from rag.embedders.ollama import OllamaEmbedder
from rag.exceptions import EmbedderConnectionError


@patch("rag.embedders.ollama.httpx.post")
def test_ollama_embedder_raises_embedder_connection_error(mock_post: object) -> None:
    mock_post.side_effect = httpx.ConnectError("refused")

    embedder = OllamaEmbedder(
        {
            "model": "nomic-embed-text",
            "base_url": "http://localhost:11434",
            "dimensions": 768,
        }
    )
    with pytest.raises(EmbedderConnectionError):
        embedder.embed("hello")
