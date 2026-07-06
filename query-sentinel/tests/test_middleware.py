"""Tests middleware et headers debug."""

from __future__ import annotations

import pytest
from django.test import Client

from query_sentinel.conf import HEADER_N_PLUS_ONE, HEADER_N_PLUS_ONE_DEBUG, HEADER_N_PLUS_ONE_SOURCE, HEADER_SQL_COUNT


@pytest.mark.django_db
def test_middleware_adds_debug_headers_on_ping(client: Client, settings: object) -> None:
    settings.DEBUG = True
    response = client.get("/ping/")
    assert response.status_code == 200
    assert HEADER_SQL_COUNT in response
    assert HEADER_N_PLUS_ONE in response


@pytest.mark.django_db
def test_middleware_detects_n_plus_one_header(client: Client, settings: object) -> None:
    settings.DEBUG = True
    from django.contrib.auth.models import User

    User.objects.create(username="u1")
    User.objects.create(username="u2")
    User.objects.create(username="u3")
    User.objects.create(username="u4")
    response = client.get("/n-plus-one/")
    assert response.status_code == 200
    assert response[HEADER_N_PLUS_ONE] == "true"
    assert HEADER_N_PLUS_ONE_SOURCE in response
    assert "n_plus_one_view" in response[HEADER_N_PLUS_ONE_SOURCE]
    assert HEADER_N_PLUS_ONE_DEBUG in response
    assert "patterns" in response[HEADER_N_PLUS_ONE_DEBUG]
