"""Formatage des rapports N+1 pour headers, logs et tests."""

from __future__ import annotations

import json
from typing import Any

from query_sentinel.schemas import AnalysisReport, QueryOrigin, RedundantPattern

_HEADER_MAX_LENGTH = 4000
_SQL_PREVIEW_LENGTH = 240


def format_origin(origin: QueryOrigin | None) -> str:
    if origin is None:
        return "unknown:0 in unknown()"
    return f"{origin.filename}:{origin.lineno} in {origin.function}()"


def format_pattern_message(pattern: RedundantPattern) -> str:
    origin = format_origin(pattern.primary_origin)
    sql_preview = pattern.sample_sql.replace("\n", " ")[:_SQL_PREVIEW_LENGTH]
    return (
        f"{pattern.execution_count}x « {pattern.normalized_sql[:100]}… » "
        f"| SQL: {sql_preview} | source: {origin}"
    )


def format_n_plus_one_message(report: AnalysisReport) -> str:
    """Message lisible pour logs console, tests ou erreurs."""
    if not report.redundant_patterns:
        return "Aucun N+1 détecté."
    lines = ["N+1 détecté :"]
    for index, pattern in enumerate(report.redundant_patterns[:3], start=1):
        lines.append(f"  {index}. {format_pattern_message(pattern)}")
        for extra_origin in pattern.origins[1:3]:
            lines.append(f"     ↳ aussi: {format_origin(extra_origin)}")
    return "\n".join(lines)


def build_debug_payload(report: AnalysisReport) -> dict[str, Any]:
    """Payload JSON compact pour header HTTP ou structlog."""
    return {
        "n_plus_one_detected": report.n_plus_one_detected,
        "sql_count": report.total_queries,
        "max_redundancy": report.max_redundancy,
        "patterns": [
            {
                "count": pattern.execution_count,
                "threshold": pattern.threshold,
                "normalized_sql": pattern.normalized_sql[:_SQL_PREVIEW_LENGTH],
                "sample_sql": pattern.sample_sql.replace("\n", " ")[:_SQL_PREVIEW_LENGTH],
                "primary_origin": format_origin(pattern.primary_origin),
                "origins": [format_origin(origin) for origin in pattern.origins[:5]],
            }
            for pattern in report.redundant_patterns[:3]
        ],
    }


def build_debug_header_value(report: AnalysisReport) -> str:
    """Valeur du header X-Django-N-Plus-One-Debug (JSON tronqué si nécessaire)."""
    payload = build_debug_payload(report)
    encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    if len(encoded) <= _HEADER_MAX_LENGTH:
        return encoded
    return encoded[: _HEADER_MAX_LENGTH - 3] + "..."
