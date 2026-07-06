"""Formatage debug pour headers, logs et tests."""

from __future__ import annotations

import json
from typing import Any

from payload_sentinel.schemas import PayloadAnalysisReport

_HEADER_MAX = 4000


def format_overfetch_message(report: PayloadAnalysisReport) -> str:
    if not report.overfetch_detected:
        return ""
    pct = int(report.overfetch_ratio * 100)
    unused = ", ".join(report.unused_columns[:8])
    return (
        f"Sur-sélection SQL : {pct}% des colonnes récupérées ne sont pas dans la réponse JSON. "
        f"Colonnes inutiles : {unused}. "
        f"Optimisation : utilisez .only() / .values() / un serializer restreint."
    )


def format_sensitive_message(report: PayloadAnalysisReport) -> str:
    if not report.sensitive_hits:
        return ""
    hits = ", ".join(f"{hit.field_path} ({hit.matched_pattern})" for hit in report.sensitive_hits[:5])
    return f"Fuite de données sensible détectée : {hits}"


def format_report_message(report: PayloadAnalysisReport) -> str:
    parts = [format_sensitive_message(report), format_overfetch_message(report)]
    return "\n".join(part for part in parts if part)


def build_debug_payload(report: PayloadAnalysisReport) -> dict[str, Any]:
    return {
        "response_parsed": report.response_parsed,
        "sql_columns_fetched": report.sql_columns_fetched[:30],
        "response_field_paths": report.response_field_paths[:30],
        "unused_columns": report.unused_columns[:20],
        "used_columns": report.used_columns[:20],
        "overfetch_ratio": report.overfetch_ratio,
        "overfetch_detected": report.overfetch_detected,
        "sensitive_leak_detected": report.sensitive_leak_detected,
        "sensitive_hits": [
            {"field_path": hit.field_path, "pattern": hit.matched_pattern}
            for hit in report.sensitive_hits[:10]
        ],
    }


def build_debug_header_value(report: PayloadAnalysisReport) -> str:
    encoded = json.dumps(build_debug_payload(report), ensure_ascii=False, separators=(",", ":"))
    if len(encoded) <= _HEADER_MAX:
        return encoded
    return encoded[: _HEADER_MAX - 3] + "..."
