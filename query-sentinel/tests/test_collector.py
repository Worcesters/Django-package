"""Tests du collecteur SQL."""

from __future__ import annotations

import pytest
from django.contrib.auth.models import User

from query_sentinel.collector import query_collection


@pytest.mark.django_db
def test_query_collection_records_orm_queries() -> None:
    User.objects.create(username="alice")
    with query_collection() as records:
        list(User.objects.filter(username="alice"))
    assert len(records) >= 1
    assert "auth_user" in records[0].sql.lower()
