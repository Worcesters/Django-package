"""Tests de l'analyseur SQL vs payload."""

from __future__ import annotations

from payload_sentinel.analyzer import analyze_payload
from payload_sentinel.schemas import PayloadSentinelConfig, SqlCapture, SqlColumn


def test_analyze_payload_detects_overfetch() -> None:
    captures = [
        SqlCapture(
            sql='SELECT "auth_user"."id", "auth_user"."password", "auth_user"."email" FROM "auth_user"',
            columns=(
                SqlColumn(table="auth_user", column="id"),
                SqlColumn(table="auth_user", column="password"),
                SqlColumn(table="auth_user", column="email"),
            ),
        )
    ]
    config = PayloadSentinelConfig(overfetch_threshold=0.5)
    report = analyze_payload(
        captures,
        response_payload={"id": 1},
        response_paths=["id"],
        config=config,
    )
    assert report.overfetch_detected is True
    assert report.overfetch_ratio >= 0.5
    assert "password" in report.unused_columns or "auth_user.password" in str(report.unused_columns)


def test_analyze_payload_detects_sensitive_field() -> None:
    config = PayloadSentinelConfig(sensitive_fields=("password_hash", "api_token"))
    report = analyze_payload(
        [],
        response_payload={"user": {"password_hash": "abc"}},
        response_paths=["user", "user.password_hash"],
        config=config,
    )
    assert report.sensitive_leak_detected is True
    assert report.sensitive_hits[0].matched_pattern == "password_hash"


def test_analyze_payload_clean_when_columns_match() -> None:
    captures = [
        SqlCapture(
            sql='SELECT "book"."id", "book"."title" FROM "book"',
            columns=(
                SqlColumn(table="book", column="id"),
                SqlColumn(table="book", column="title"),
            ),
        )
    ]
    config = PayloadSentinelConfig(overfetch_threshold=0.85)
    report = analyze_payload(
        captures,
        response_payload={"id": 1, "title": "Dune"},
        response_paths=["id", "title"],
        config=config,
    )
    assert report.overfetch_detected is False
    assert report.sensitive_leak_detected is False
