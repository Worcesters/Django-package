"""Tests du collecteur SQL."""

from __future__ import annotations

import pytest
from django.contrib.auth.models import User

from payload_sentinel.collector import sql_column_collection


@pytest.mark.django_db
def test_sql_column_collection_records_orm_queries() -> None:
    User.objects.create(username="alice")
    with sql_column_collection() as captures:
        list(User.objects.filter(username="alice"))
    assert len(captures) >= 1
    assert captures[0].columns
    assert "auth_user" in captures[0].sql.lower() or any(
        col.column for col in captures[0].columns
    )
