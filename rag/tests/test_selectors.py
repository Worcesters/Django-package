"""Tests des selectors rag."""

from __future__ import annotations

from django.test import override_settings

from rag.selectors import get_chunking_config


@override_settings(RAG_CHUNKING={"words_per_chunk": "42"})
def test_get_chunking_config_coerces_words_per_chunk_to_int() -> None:
    config = get_chunking_config()
    assert config.words_per_chunk == 42
    assert isinstance(config.words_per_chunk, int)


@override_settings(RAG_CHUNKING={"words_per_chunk": None})
def test_get_chunking_config_accepts_none_words_per_chunk() -> None:
    config = get_chunking_config()
    assert config.words_per_chunk is None
