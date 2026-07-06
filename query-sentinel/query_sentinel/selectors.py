"""Lecture de la configuration (couche selector)."""

from __future__ import annotations

from query_sentinel.conf import (
    SETTING_BLOCK_STAGING,
    SETTING_DEBUG_HEADERS,
    SETTING_ENABLED,
    SETTING_MAX_QUERIES,
    SETTING_N_PLUS_ONE_THRESHOLD,
    SETTING_REDUNDANCY_LOG_THRESHOLD,
    SETTING_STRICT_IN_TESTS,
    SETTING_STRUCTLOG_ENABLED,
)
from query_sentinel.schemas import SentinelConfig
from query_sentinel.settings_source import get_setting


def get_sentinel_config() -> SentinelConfig:
    """Construit la configuration résolue depuis Django ou JSON."""
    return SentinelConfig(
        enabled=bool(get_setting(SETTING_ENABLED, default=True)),
        n_plus_one_threshold=int(get_setting(SETTING_N_PLUS_ONE_THRESHOLD, default=3)),
        max_queries_per_request=_optional_int(get_setting(SETTING_MAX_QUERIES, default=None)),
        debug_headers=bool(get_setting(SETTING_DEBUG_HEADERS, default=True)),
        strict_in_tests=bool(get_setting(SETTING_STRICT_IN_TESTS, default=False)),
        structlog_enabled=bool(get_setting(SETTING_STRUCTLOG_ENABLED, default=True)),
        redundancy_log_threshold=int(get_setting(SETTING_REDUNDANCY_LOG_THRESHOLD, default=5)),
        block_on_n_plus_one_staging=bool(get_setting(SETTING_BLOCK_STAGING, default=False)),
    )


def _optional_int(value: object) -> int | None:
    if value is None:
        return None
    return int(value)
