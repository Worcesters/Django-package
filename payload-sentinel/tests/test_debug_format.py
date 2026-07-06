"""Tests debug_format."""

from __future__ import annotations

from payload_sentinel.debug_format import (
    build_debug_payload,
    format_overfetch_message,
    format_sensitive_message,
)
from payload_sentinel.schemas import PayloadAnalysisReport, SensitiveHit


def test_format_overfetch_message() -> None:
    report = PayloadAnalysisReport(
        overfetch_detected=True,
        overfetch_ratio=0.9,
        unused_columns=["password", "email"],
    )
    message = format_overfetch_message(report)
    assert "90%" in message
    assert ".only()" in message


def test_format_sensitive_message() -> None:
    report = PayloadAnalysisReport(
        sensitive_hits=[SensitiveHit(field_path="password_hash", matched_pattern="password")],
    )
    message = format_sensitive_message(report)
    assert "password_hash" in message


def test_build_debug_payload() -> None:
    report = PayloadAnalysisReport(
        sql_columns_fetched=["id", "password"],
        response_field_paths=["id"],
        overfetch_ratio=0.5,
    )
    payload = build_debug_payload(report)
    assert payload["sql_columns_fetched"] == ["id", "password"]
    assert payload["overfetch_ratio"] == 0.5
