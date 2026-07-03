"""Fixtures Pytest pour le package rag."""

from __future__ import annotations

import pytest

from rag.stores.memory import InMemoryStore


@pytest.fixture(autouse=True)
def clear_memory_store() -> None:
    """Isole les tests en vidant le store en mémoire partagé."""
    InMemoryStore._shared_data.clear()
    yield
    InMemoryStore._shared_data.clear()
