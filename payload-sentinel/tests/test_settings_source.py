"""Tests settings_source."""

from __future__ import annotations

from pathlib import Path

import pytest

from payload_sentinel.selectors import get_payload_config
from payload_sentinel.settings_source import (
    configure_from_dict,
    get_setting,
    reset_configuration,
)


@pytest.fixture(autouse=True)
def _reset_config() -> None:
    reset_configuration()
    yield
    reset_configuration()


def test_configure_from_dict() -> None:
    configure_from_dict({"PAYLOAD_SENTINEL_OVERFETCH_THRESHOLD": 0.5})
    assert get_setting("PAYLOAD_SENTINEL_OVERFETCH_THRESHOLD") == 0.5


def test_get_payload_config_from_dict() -> None:
    configure_from_dict(
        {
            "PAYLOAD_SENTINEL_ENABLED": False,
            "PAYLOAD_SENTINEL_OVERFETCH_THRESHOLD": 0.6,
        }
    )
    config = get_payload_config()
    assert config.enabled is False
    assert config.overfetch_threshold == 0.6


def test_configure_from_file() -> None:
    config_path = Path(__file__).parent / "config" / "payload.test.json"
    from payload_sentinel.settings_source import configure_from_file

    configure_from_file(config_path)
    config = get_payload_config()
    assert config.overfetch_threshold == 0.5
    assert config.block_sensitive_leak is False
