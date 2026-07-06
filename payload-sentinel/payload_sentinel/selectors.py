"""Lecture de la configuration (couche selector)."""

from __future__ import annotations

from payload_sentinel.conf import (
    DEFAULT_SENSITIVE_FIELDS,
    SETTING_BLOCK_SENSITIVE_LEAK,
    SETTING_DEBUG_HEADERS,
    SETTING_ENABLED,
    SETTING_LOG_OVERFETCH,
    SETTING_OVERFETCH_THRESHOLD,
    SETTING_SENSITIVE_FIELDS,
    SETTING_STRICT_IN_TESTS,
    SETTING_STRUCTLOG_ENABLED,
)
from payload_sentinel.schemas import PayloadSentinelConfig
from payload_sentinel.settings_source import get_setting


def get_payload_config() -> PayloadSentinelConfig:
    raw_sensitive = get_setting(SETTING_SENSITIVE_FIELDS, default=list(DEFAULT_SENSITIVE_FIELDS))
    sensitive = tuple(str(item).lower() for item in raw_sensitive)
    return PayloadSentinelConfig(
        enabled=bool(get_setting(SETTING_ENABLED, default=True)),
        sensitive_fields=sensitive,
        overfetch_threshold=float(get_setting(SETTING_OVERFETCH_THRESHOLD, default=0.85)),
        block_sensitive_leak=bool(get_setting(SETTING_BLOCK_SENSITIVE_LEAK, default=True)),
        debug_headers=bool(get_setting(SETTING_DEBUG_HEADERS, default=True)),
        structlog_enabled=bool(get_setting(SETTING_STRUCTLOG_ENABLED, default=True)),
        log_overfetch=bool(get_setting(SETTING_LOG_OVERFETCH, default=True)),
        strict_in_tests=bool(get_setting(SETTING_STRICT_IN_TESTS, default=False)),
    )
