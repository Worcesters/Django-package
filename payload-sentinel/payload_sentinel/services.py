"""Logique métier — analyse payload et application des politiques."""

from __future__ import annotations

import json
from typing import Any

from django.http import HttpResponse

from payload_sentinel.analyzer import analyze_payload
from payload_sentinel.collector import sql_column_collection
from payload_sentinel.debug_format import format_overfetch_message, format_report_message
from payload_sentinel.exceptions import OverfetchWarning, SensitiveDataLeakError
from payload_sentinel.response_inspector import parse_json_response
from payload_sentinel.schemas import PayloadAnalysisReport, PayloadSentinelConfig, SqlCapture


def build_payload_report(
    captures: list[SqlCapture],
    response: HttpResponse,
    config: PayloadSentinelConfig,
) -> PayloadAnalysisReport:
    payload, paths = _extract_response_data(response)
    return analyze_payload(
        captures,
        response_payload=payload,
        response_paths=paths,
        config=config,
    )


def _extract_response_data(response: HttpResponse) -> tuple[object | None, list[str]]:
    content_type = response.get("Content-Type", "")
    if "json" not in content_type.lower():
        return None, []
    if not hasattr(response, "content"):
        return None, []
    return parse_json_response(response.content)


def enforce_policies(
    report: PayloadAnalysisReport,
    config: PayloadSentinelConfig,
    *,
    strict: bool | None = None,
) -> None:
    """Applique les politiques de sécurité et de performance."""
    is_strict = config.strict_in_tests if strict is None else strict

    if report.sensitive_leak_detected and config.block_sensitive_leak:
        raise SensitiveDataLeakError(
            format_report_message(report) or "Fuite de données sensible détectée.",
            component="security",
        )

    if report.overfetch_detected and is_strict:
        raise OverfetchWarning(
            format_overfetch_message(report) or "Sur-sélection SQL détectée.",
            component="performance",
        )


def block_sensitive_response(report: PayloadAnalysisReport) -> HttpResponse:
    body = {
        "error": "sensitive_data_leak_blocked",
        "message": format_sensitive_only(report),
    }
    return HttpResponse(
        json.dumps(body, ensure_ascii=False),
        status=500,
        content_type="application/json",
    )


def format_sensitive_only(report: PayloadAnalysisReport) -> str:
    from payload_sentinel.debug_format import format_sensitive_message

    return format_sensitive_message(report) or "Champ sensible détecté dans la réponse API."


def inspect_request_cycle(
    get_response: Any,
    request: Any,
    config: PayloadSentinelConfig,
) -> tuple[HttpResponse, PayloadAnalysisReport, list[SqlCapture]]:
    with sql_column_collection() as captures:
        response = get_response(request)
    report = build_payload_report(captures, response, config)
    return response, report, captures
