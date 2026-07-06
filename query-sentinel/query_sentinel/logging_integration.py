"""Intégration structlog / logging JSON pour alertes production."""

from __future__ import annotations

import json
import logging
from typing import Any

from query_sentinel.schemas import AnalysisReport

logger = logging.getLogger("query_sentinel")


def log_analysis_event(
    report: AnalysisReport,
    *,
    path: str | None = None,
    method: str | None = None,
    view_name: str | None = None,
) -> None:
    """Logue un événement de redondance SQL (structlog si disponible, sinon stdlib JSON)."""
    payload: dict[str, Any] = {
        "event": "query_sentinel_redundancy",
        "sql_count": report.total_queries,
        "n_plus_one_detected": report.n_plus_one_detected,
        "max_redundancy": report.max_redundancy,
        "redundant_patterns": [
            {
                "count": pattern.execution_count,
                "normalized_sql": pattern.normalized_sql[:500],
            }
            for pattern in report.redundant_patterns[:5]
        ],
        "path": path,
        "method": method,
        "view_name": view_name,
    }

    try:
        import structlog

        structlog.get_logger("query_sentinel").warning("sql_redundancy_detected", **payload)
    except ImportError:
        logger.warning(json.dumps(payload, ensure_ascii=False))
