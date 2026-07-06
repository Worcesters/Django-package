"""Middleware Django — compare SQL vs payload JSON."""

from __future__ import annotations

import logging
from typing import Callable

from django.conf import settings as django_settings
from django.http import HttpRequest, HttpResponse

from payload_sentinel.conf import (
    HEADER_DEBUG,
    HEADER_OVERFETCH_RATIO,
    HEADER_RESPONSE_FIELDS,
    HEADER_SENSITIVE_LEAK,
    HEADER_SQL_COLUMNS,
)
from payload_sentinel.debug_format import build_debug_header_value, format_report_message
from payload_sentinel.exceptions import SensitiveDataLeakError
from payload_sentinel.logging_integration import log_payload_event
from payload_sentinel.selectors import get_payload_config
from payload_sentinel.services import (
    block_sensitive_response,
    build_payload_report,
    enforce_policies,
)
from payload_sentinel.collector import sql_column_collection

logger = logging.getLogger("payload_sentinel")


class PayloadSentinelMiddleware:
    """Surveillance passive : colonnes SQL vs champs JSON renvoyés."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        config = get_payload_config()
        if not config.enabled:
            return self.get_response(request)

        with sql_column_collection() as captures:
            response = self.get_response(request)

        report = build_payload_report(captures, response, config)

        if config.debug_headers and django_settings.DEBUG:
            _attach_debug_headers(response, report)
            message = format_report_message(report)
            if message:
                logger.warning(message)

        if config.structlog_enabled and (
            report.sensitive_leak_detected
            or (report.overfetch_detected and config.log_overfetch)
        ):
            log_payload_event(
                report,
                path=getattr(request, "path", None),
                method=getattr(request, "method", None),
            )

        try:
            enforce_policies(report, config)
        except SensitiveDataLeakError:
            return block_sensitive_response(report)

        return response


def _attach_debug_headers(response: HttpResponse, report: object) -> None:
    from payload_sentinel.schemas import PayloadAnalysisReport

    assert isinstance(report, PayloadAnalysisReport)
    response[HEADER_SQL_COLUMNS] = str(len(report.sql_columns_fetched))
    response[HEADER_RESPONSE_FIELDS] = str(len(report.response_field_paths))
    response[HEADER_OVERFETCH_RATIO] = str(report.overfetch_ratio)
    response[HEADER_SENSITIVE_LEAK] = str(report.sensitive_leak_detected).lower()
    response[HEADER_DEBUG] = build_debug_header_value(report)
