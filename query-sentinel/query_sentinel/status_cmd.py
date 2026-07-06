"""Commande CLI : affiche la configuration active."""

from __future__ import annotations

import json

from query_sentinel.selectors import get_sentinel_config
from query_sentinel.settings_source import bootstrap_runtime


def run_status(
    *,
    settings_module: str | None = None,
    config_path: str | None = None,
) -> None:
    """Affiche la configuration query-sentinel résolue."""
    bootstrap_runtime(settings_module=settings_module, config_path=config_path)
    config = get_sentinel_config()
    payload = {
        "enabled": config.enabled,
        "n_plus_one_threshold": config.n_plus_one_threshold,
        "max_queries_per_request": config.max_queries_per_request,
        "debug_headers": config.debug_headers,
        "strict_in_tests": config.strict_in_tests,
        "structlog_enabled": config.structlog_enabled,
        "redundancy_log_threshold": config.redundancy_log_threshold,
        "block_on_n_plus_one_staging": config.block_on_n_plus_one_staging,
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
