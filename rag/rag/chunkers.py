"""Découpage de texte avant embedding."""

from __future__ import annotations

import re

from rag.exceptions import ChunkingError
from rag.schemas import Chunk, ChunkingConfig


def chunk_text(text: str, config: ChunkingConfig) -> list[Chunk]:
    """Découpe un texte selon la stratégie configurée."""
    stripped = text.strip()
    if not stripped:
        return []

    strategy = config.strategy.lower()
    if strategy == "fixed_size":
        return _chunk_fixed_size(stripped, config)
    if strategy == "sentence":
        return _chunk_by_sentence(stripped, config)
    if strategy == "paragraph":
        return _chunk_by_paragraph(stripped, config)
    if strategy == "word":
        return _chunk_by_word(stripped, config)
    raise ChunkingError(f"Stratégie de chunking inconnue : '{config.strategy}'.")


def _chunk_fixed_size(text: str, config: ChunkingConfig) -> list[Chunk]:
    size = max(config.chunk_size, 1)
    overlap = min(max(config.chunk_overlap, 0), size - 1)
    chunks: list[Chunk] = []
    start = 0
    index = 0
    while start < len(text):
        end = min(start + size, len(text))
        piece = text[start:end].strip()
        if piece:
            chunks.append(Chunk(text=piece, index=index))
            index += 1
        if end >= len(text):
            break
        start = end - overlap
    return chunks


def _chunk_by_paragraph(text: str, config: ChunkingConfig) -> list[Chunk]:
    separator = config.separators[0] if config.separators else "\n\n"
    parts = [part.strip() for part in text.split(separator) if part.strip()]
    return [Chunk(text=part, index=i) for i, part in enumerate(parts)]


def _chunk_by_sentence(text: str, config: ChunkingConfig) -> list[Chunk]:
    parts = re.split(r"(?<=[.!?])\s+", text)
    parts = [part.strip() for part in parts if part.strip()]
    return [Chunk(text=part, index=i) for i, part in enumerate(parts)]


def _chunk_by_word(text: str, config: ChunkingConfig) -> list[Chunk]:
    words = text.split()
    size = config.words_per_chunk or 50
    chunks: list[Chunk] = []
    for index in range(0, len(words), size):
        piece = " ".join(words[index : index + size])
        if piece:
            chunks.append(Chunk(text=piece, index=len(chunks)))
    return chunks
