"""Décorateurs pour le mode strict en tests."""

from __future__ import annotations

import functools
from collections.abc import Callable
from typing import Any, TypeVar

from django.http import HttpResponse

from payload_sentinel.collector import sql_column_collection
from payload_sentinel.debug_format import format_overfetch_message, format_report_message, format_sensitive_message
from payload_sentinel.exceptions import OverfetchWarning, SensitiveDataLeakError
from payload_sentinel.selectors import get_payload_config
from payload_sentinel.services import build_payload_report, enforce_policies

F = TypeVar("F", bound=Callable[..., Any])


def _coerce_response(result: Any) -> HttpResponse:
    if isinstance(result, HttpResponse):
        return result
    raise TypeError(
        "Le décorateur payload-sentinel attend un HttpResponse en retour "
        "(ex. self.client.get(...))."
    )


def fail_on_overfetch() -> Callable[[F], F]:
    """Échoue si sur-sélection SQL détectée (le test doit retourner HttpResponse)."""

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            config = get_payload_config()
            with sql_column_collection() as captures:
                result = func(*args, **kwargs)
            response = _coerce_response(result)
            report = build_payload_report(captures, response, config)
            try:
                enforce_policies(report, config, strict=True)
            except OverfetchWarning as exc:
                raise AssertionError(format_overfetch_message(report)) from exc
            except SensitiveDataLeakError as exc:
                raise AssertionError(format_sensitive_message(report)) from exc
            return result

        return wrapper  # type: ignore[return-value]

    return decorator


def fail_on_sensitive_leak() -> Callable[[F], F]:
    """Échoue si fuite de données sensible détectée."""

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            config = get_payload_config()
            with sql_column_collection() as captures:
                result = func(*args, **kwargs)
            response = _coerce_response(result)
            report = build_payload_report(captures, response, config)
            if report.sensitive_leak_detected:
                raise AssertionError(format_sensitive_message(report))
            return result

        return wrapper  # type: ignore[return-value]

    return decorator


def payload_sentinel_guard() -> Callable[[F], F]:
    """Échoue sur sur-sélection SQL ou fuite sensible."""

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            config = get_payload_config()
            with sql_column_collection() as captures:
                result = func(*args, **kwargs)
            response = _coerce_response(result)
            report = build_payload_report(captures, response, config)
            try:
                enforce_policies(report, config, strict=True)
            except (OverfetchWarning, SensitiveDataLeakError) as exc:
                raise AssertionError(format_report_message(report)) from exc
            return result

        return wrapper  # type: ignore[return-value]

    return decorator
