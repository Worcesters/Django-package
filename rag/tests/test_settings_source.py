"""Tests de settings_source (standalone + Django)."""

from __future__ import annotations

from pathlib import Path

import pytest

from rag.conf import SETTING_DEFAULT_EMBEDDER, SETTING_EMBEDDERS
from rag.exceptions import ConfigurationError
from rag.selectors import get_embedder_config, get_store_config
from rag.settings_source import (
    configure_from_dict,
    configure_from_file,
    get_setting,
    reset_configuration,
)

_CONFIG_DIR = Path(__file__).resolve().parent / "config"
_RAG_JSON = _CONFIG_DIR / "rag.test.json"


@pytest.fixture(autouse=True)
def _reset_config() -> None:
    reset_configuration()
    yield
    reset_configuration()


def test_configure_from_file_loads_embedders() -> None:
    configure_from_file(_RAG_JSON)
    assert get_setting(SETTING_DEFAULT_EMBEDDER) == "ollama"
    embedders = get_setting(SETTING_EMBEDDERS)
    assert "ollama" in embedders


def test_get_embedder_config_from_json_without_django() -> None:
    configure_from_file(_RAG_JSON)
    config = get_embedder_config("ollama")
    assert config.embedder == "ollama"
    assert config.dimensions == 3


def test_get_store_config_from_json_without_django() -> None:
    configure_from_file(_RAG_JSON)
    config = get_store_config()
    assert config.store == "memory"
    assert config.dimensions == 3


def test_get_setting_raises_for_missing_key_in_json() -> None:
    configure_from_dict({"RAG_DEFAULT_EMBEDDER": "ollama"})
    with pytest.raises(ConfigurationError, match="absente du fichier"):
        get_setting(SETTING_EMBEDDERS)
