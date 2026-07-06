"""Intégration structlog / logging JSON."""

from __future__ import annotations

import json
import logging
from typing import Any

from payload_sentinel.debug_format import build_debug_payload
from payload_sentinel.schemas import PayloadAnalysisReport

logger = logging.getLogger("payload_sentinel")


def log_payload_event(
    report: PayloadAnalysisReport,
    *,
    path: str | None = None,
    method: str | None = None,
) -> None:
    payload: dict[str, Any] = {
        "event": "payload_sentinel_alert",
        **build_debug_payload(report),
        "path": path,
        "method": method,
    }
    try:
        import structlog

        structlog.get_logger("payload_sentinel").warning("payload_alert", **payload)
    except ImportError:
        logger.warning(json.dumps(payload, ensure_ascii=False))
