"""Middleware Django — collecte SQL, headers debug, alertes production."""

from __future__ import annotations

import logging
from typing import Callable

from django.conf import settings as django_settings
from django.http import HttpRequest, HttpResponse

from query_sentinel.collector import query_collection
from query_sentinel.conf import (
    HEADER_MAX_REDUNDANCY,
    HEADER_N_PLUS_ONE,
    HEADER_N_PLUS_ONE_DEBUG,
    HEADER_N_PLUS_ONE_SOURCE,
    HEADER_SQL_COUNT,
)
from query_sentinel.debug_format import (
    build_debug_header_value,
    format_n_plus_one_message,
    format_origin,
)
from query_sentinel.logging_integration import log_analysis_event
from query_sentinel.selectors import get_sentinel_config
from query_sentinel.services import build_analysis_report, enforce_policies, should_log_redundancy

logger = logging.getLogger("query_sentinel")


class QuerySentinelMiddleware:
    """Surveillance passive des requêtes SQL pendant le cycle HTTP."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        config = get_sentinel_config()
        if not config.enabled:
            return self.get_response(request)

        with query_collection() as records:
            response = self.get_response(request)

        report = build_analysis_report(records, config)

        if config.debug_headers and django_settings.DEBUG:
            response[HEADER_SQL_COUNT] = str(report.total_queries)
            response[HEADER_N_PLUS_ONE] = str(report.n_plus_one_detected).lower()
            response[HEADER_MAX_REDUNDANCY] = str(report.max_redundancy)
            if report.n_plus_one_detected and report.redundant_patterns:
                top = report.redundant_patterns[0]
                response[HEADER_N_PLUS_ONE_SOURCE] = format_origin(top.primary_origin)
                response[HEADER_N_PLUS_ONE_DEBUG] = build_debug_header_value(report)
                logger.warning(format_n_plus_one_message(report))

        if should_log_redundancy(report, config):
            log_analysis_event(
                report,
                path=getattr(request, "path", None),
                method=getattr(request, "method", None),
                view_name=_resolve_view_name(request),
            )

        enforce_policies(
            report,
            config,
            strict=config.block_on_n_plus_one_staging,
        )
        return response


def _resolve_view_name(request: HttpRequest) -> str | None:
    resolver_match = getattr(request, "resolver_match", None)
    if resolver_match is None:
        return None
    view_func = getattr(resolver_match, "func", None)
    return getattr(view_func, "__qualname__", None)
