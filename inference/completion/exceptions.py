"""Exceptions métier du package inference."""

from __future__ import annotations


class InferenceError(Exception):
    code: str = "inference_error"

    def __init__(
        self,
        message: str,
        *,
        provider: str | None = None,
        code: str | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.provider = provider
        if code is not None:
            self.code = code


class ProviderNotFoundError(InferenceError):
    code = "provider_not_found"


class ConfigurationError(InferenceError):
    code = "configuration_error"


class ProviderConnectionError(InferenceError):
    code = "provider_connection_error"


class ProviderAPIError(InferenceError):
    code = "provider_api_error"


class ParseError(InferenceError):
    code = "parse_error"


class RateLimitError(InferenceError):
    code = "rate_limit_error"
