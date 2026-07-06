"""Tests des décorateurs stricts."""

from __future__ import annotations

import pytest
from django.contrib.auth.models import User
from django.http import JsonResponse

from payload_sentinel.decorators import fail_on_overfetch, fail_on_sensitive_leak


@pytest.mark.django_db
def test_fail_on_sensitive_leak_raises() -> None:
    @fail_on_sensitive_leak()
    def build_leak_response() -> object:
        return JsonResponse({"username": "alice", "password_hash": "secret"})

    with pytest.raises(AssertionError, match="Fuite"):
        build_leak_response()


@pytest.mark.django_db
def test_fail_on_overfetch_raises() -> None:
    @fail_on_overfetch()
    def build_overfetch_response() -> object:
        user = User.objects.create(username="carol")
        fetched = User.objects.get(pk=user.pk)
        return JsonResponse({"id": fetched.id})

    with pytest.raises(AssertionError, match="Sur-sélection"):
        build_overfetch_response()
