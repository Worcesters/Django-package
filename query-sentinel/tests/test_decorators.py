"""Tests du décorateur fail_on_n_plus_one."""

from __future__ import annotations

import pytest
from django.db import connection

from query_sentinel.decorators import fail_on_n_plus_one
from query_sentinel.settings_source import configure_from_dict, reset_configuration


@pytest.fixture(autouse=True)
def _reset() -> None:
    reset_configuration()
    yield
    reset_configuration()


@fail_on_n_plus_one(threshold=2)
def _run_repeated_queries() -> int:
    with connection.cursor() as cursor:
        for value in (1, 2, 3):
            cursor.execute("SELECT 1 WHERE %s = %s", [value, value])
    return 3


@pytest.mark.django_db
def test_fail_on_n_plus_one_raises_assertion() -> None:
    configure_from_dict({"QUERY_SENTINEL_N_PLUS_ONE_THRESHOLD": 2})
    with pytest.raises(AssertionError, match="_run_repeated_queries"):
        _run_repeated_queries()


@pytest.mark.django_db
def test_fail_on_n_plus_one_passes_when_clean() -> None:
    configure_from_dict({"QUERY_SENTINEL_N_PLUS_ONE_THRESHOLD": 5})

    @fail_on_n_plus_one(threshold=5)
    def clean() -> None:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")

    clean()
