"""Tests de settings_source (standalone + Django)."""

from __future__ import annotations

from pathlib import Path

import pytest

from completion.conf import SETTING_DEFAULT_PROVIDER, SETTING_PROVIDERS
from completion.exceptions import ConfigurationError
from completion.selectors import get_provider_config
from completion.settings_source import (
    configure_from_dict,
    configure_from_file,
    get_setting,
    reset_configuration,
)

_CONFIG_DIR = Path(__file__).resolve().parent / "config"
_INFERENCE_JSON = _CONFIG_DIR / "inference.test.json"


@pytest.fixture(autouse=True)
def _reset_config() -> None:
    reset_configuration()
    yield
    reset_configuration()


def test_configure_from_file_loads_providers() -> None:
    configure_from_file(_INFERENCE_JSON)
    assert get_setting(SETTING_DEFAULT_PROVIDER) == "llama"
    providers = get_setting(SETTING_PROVIDERS)
    assert "llama" in providers


def test_get_provider_config_from_json_without_django() -> None:
    configure_from_file(_INFERENCE_JSON)
    config = get_provider_config("llama")
    assert config.provider == "llama"
    assert config.model == "llama3.2"
    assert config.base_url == "http://localhost:11434"


def test_configure_from_dict_overrides_django(settings: object) -> None:
    configure_from_dict(
        {
            SETTING_DEFAULT_PROVIDER: "openai",
            SETTING_PROVIDERS: {
                "openai": {
                    "model": "gpt-4o",
                    "api_key": "test-key",
                    "base_url": "https://api.openai.com/v1",
                },
            },
        }
    )
    config = get_provider_config()
    assert config.provider == "openai"
    assert config.api_key == "test-key"


def test_get_setting_raises_for_missing_key_in_json() -> None:
    configure_from_dict({"INFERENCE_DEFAULT_PROVIDER": "openai"})
    with pytest.raises(ConfigurationError, match="absente du fichier"):
        get_setting(SETTING_PROVIDERS)


def test_configure_from_file_missing_raises() -> None:
    with pytest.raises(ConfigurationError, match="introuvable"):
        configure_from_file("/nonexistent/inference.json")
