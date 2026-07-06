"""Exceptions métier du package payload-sentinel."""

from __future__ import annotations


class PayloadSentinelError(Exception):
    code: str = "payload_sentinel_error"

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


class ConfigurationError(PayloadSentinelError):
    code = "configuration_error"


class SensitiveDataLeakError(PayloadSentinelError):
    code = "sensitive_data_leak"


class OverfetchWarning(PayloadSentinelError):
    code = "overfetch_detected"
