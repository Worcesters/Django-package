"""Tests de l'inspecteur de réponse JSON."""

from __future__ import annotations

from payload_sentinel.response_inspector import (
    detect_sensitive_fields,
    flatten_field_paths,
    parse_json_response,
)


def test_flatten_field_paths_nested() -> None:
    payload = {"user": {"id": 1, "email": "a@b.c"}, "items": [{"title": "x"}]}
    paths = flatten_field_paths(payload)
    assert "user" in paths
    assert "user.id" in paths
    assert "user.email" in paths


def test_detect_sensitive_fields() -> None:
    payload = {"username": "alice", "password_hash": "secret"}
    hits = detect_sensitive_fields(payload, ("password_hash",))
    assert len(hits) == 1
    assert hits[0].field_path == "password_hash"


def test_parse_json_response() -> None:
    payload, paths = parse_json_response(b'{"id": 1, "title": "Hi"}')
    assert payload == {"id": 1, "title": "Hi"}
    assert "id" in paths
    assert "title" in paths
