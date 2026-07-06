"""Mixin pytest/Django TestCase pour le mode strict."""

from __future__ import annotations

from typing import Any

from query_sentinel.collector import query_collection
from query_sentinel.exceptions import NPlusOneError
from query_sentinel.selectors import get_sentinel_config
from query_sentinel.services import build_analysis_report, enforce_policies


class SentinelTestMixin:
    """
    Mixin de test : enveloppe chaque test dans query_collection et fail on N+1.

    Usage :
        class MyTests(SentinelTestMixin, TestCase):
            ...
    """

    def run(self, result: Any) -> Any:
        config = get_sentinel_config()
        if not config.strict_in_tests:
            return super().run(result)  # type: ignore[misc]

        with query_collection() as records:
            outcome = super().run(result)  # type: ignore[misc]

        report = build_analysis_report(records, config)
        try:
            enforce_policies(report, config, strict=True)
        except NPlusOneError as exc:
            result.addError(self, (NPlusOneError, exc, exc.__traceback__))
        return outcome
