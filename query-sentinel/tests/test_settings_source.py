"""Tests settings_source."""

from __future__ import annotations

from pathlib import Path

import pytest

from query_sentinel.conf import SETTING_N_PLUS_ONE_THRESHOLD
from query_sentinel.exceptions import ConfigurationError
from query_sentinel.selectors import get_sentinel_config
from query_sentinel.settings_source import configure_from_file, get_setting, reset_configuration

_CONFIG = Path(__file__).resolve().parent / "config" / "sentinel.test.json"


@pytest.fixture(autouse=True)
def _reset() -> None:
    reset_configuration()
    yield
    reset_configuration()


def test_configure_from_file_loads_threshold() -> None:
    configure_from_file(_CONFIG)
    assert get_setting(SETTING_N_PLUS_ONE_THRESHOLD) == 3


def test_get_sentinel_config_from_json() -> None:
    configure_from_file(_CONFIG)
    config = get_sentinel_config()
    assert config.enabled is True
    assert config.n_plus_one_threshold == 3


def test_missing_key_in_json_raises() -> None:
    configure_from_file(_CONFIG)
    with pytest.raises(ConfigurationError, match="absente"):
        get_setting("QUERY_SENTINEL_DOES_NOT_EXIST")
