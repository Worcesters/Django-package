"""Tests middleware et headers debug."""

from __future__ import annotations

import json

import pytest
from django.test import Client

from payload_sentinel.conf import (
    HEADER_DEBUG,
    HEADER_OVERFETCH_RATIO,
    HEADER_SENSITIVE_LEAK,
    HEADER_SQL_COLUMNS,
)


@pytest.mark.django_db
def test_middleware_adds_debug_headers_on_ping(client: Client, settings: object) -> None:
    settings.DEBUG = True
    response = client.get("/ping/")
    assert response.status_code == 200
    assert HEADER_SQL_COLUMNS in response
    assert HEADER_OVERFETCH_RATIO in response
    assert HEADER_SENSITIVE_LEAK in response


@pytest.mark.django_db
def test_middleware_detects_overfetch(client: Client, settings: object) -> None:
    settings.DEBUG = True
    response = client.get("/overfetch/")
    assert response.status_code == 200
    assert float(response[HEADER_OVERFETCH_RATIO]) >= 0.75
    assert HEADER_DEBUG in response
    debug = json.loads(response[HEADER_DEBUG])
    assert debug["overfetch_detected"] is True


@pytest.mark.django_db
def test_middleware_blocks_sensitive_leak(client: Client, settings: object) -> None:
    settings.DEBUG = True
    response = client.get("/sensitive-leak/")
    assert response.status_code == 500
    body = json.loads(response.content)
    assert body["error"] == "sensitive_data_leak_blocked"
