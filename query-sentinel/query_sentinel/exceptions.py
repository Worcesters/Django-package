"""Exceptions métier du package query-sentinel."""

from __future__ import annotations


class SentinelError(Exception):
    code: str = "sentinel_error"

    def __init__(
        self,
        message: str,
        *,
        component: str | None = None,
        code: str | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.component = component
        if code is not None:
            self.code = code


class ConfigurationError(SentinelError):
    code = "configuration_error"


class NPlusOneError(SentinelError):
    code = "n_plus_one_detected"


class QueryBudgetExceededError(SentinelError):
    code = "query_budget_exceeded"
