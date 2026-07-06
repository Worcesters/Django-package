"""Commande CLI : affiche la configuration active."""

from __future__ import annotations

import json

from payload_sentinel.selectors import get_payload_config
from payload_sentinel.settings_source import bootstrap_runtime


def run_status(
    *,
    settings_module: str | None = None,
    config_path: str | None = None,
) -> None:
    """Affiche la configuration payload-sentinel résolue."""
    bootstrap_runtime(settings_module=settings_module, config_path=config_path)
    config = get_payload_config()
    payload = {
        "enabled": config.enabled,
        "sensitive_fields": list(config.sensitive_fields),
        "overfetch_threshold": config.overfetch_threshold,
        "block_sensitive_leak": config.block_sensitive_leak,
        "debug_headers": config.debug_headers,
        "structlog_enabled": config.structlog_enabled,
        "log_overfetch": config.log_overfetch,
        "strict_in_tests": config.strict_in_tests,
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
