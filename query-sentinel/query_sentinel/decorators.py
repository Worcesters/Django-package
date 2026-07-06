"""Décorateurs pour le mode strict en tests."""

from __future__ import annotations

import functools
from collections.abc import Callable
from typing import Any, TypeVar

from query_sentinel.collector import query_collection
from query_sentinel.exceptions import NPlusOneError
from query_sentinel.selectors import get_sentinel_config
from query_sentinel.services import build_analysis_report, enforce_policies

F = TypeVar("F", bound=Callable[..., Any])


def fail_on_n_plus_one(*, threshold: int | None = None) -> Callable[[F], F]:
    """
    Décorateur de test : échoue si un motif SQL est exécuté >= threshold fois.

    Usage :
        @fail_on_n_plus_one()
        def test_list_authors(self): ...
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            config = get_sentinel_config()
            if threshold is not None:
                config = _replace_threshold(config, threshold)

            with query_collection() as records:
                result = func(*args, **kwargs)

            report = build_analysis_report(records, config)
            try:
                enforce_policies(report, config, strict=True)
            except NPlusOneError as exc:
                top = report.redundant_patterns[0] if report.redundant_patterns else None
                detail = f" ({top.execution_count}x)" if top else ""
                raise AssertionError(f"{exc.message}{detail}") from exc
            return result

        return wrapper  # type: ignore[return-value]

    return decorator


def _replace_threshold(config: object, threshold: int) -> Any:
    from dataclasses import replace

    from query_sentinel.schemas import SentinelConfig

    assert isinstance(config, SentinelConfig)
    return replace(config, n_plus_one_threshold=threshold)
