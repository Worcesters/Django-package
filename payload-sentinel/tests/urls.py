"""URLs minimales pour les tests."""

from __future__ import annotations

from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.urls import path


def ping_view(request: object) -> HttpResponse:
    return JsonResponse({"status": "ok"})


def overfetch_view(request: object) -> HttpResponse:
    """Charge toutes les colonnes User mais ne renvoie que id."""
    user = User.objects.create(username="alice")
    fetched = User.objects.get(pk=user.pk)
    return JsonResponse({"id": fetched.id})


def sensitive_leak_view(request: object) -> HttpResponse:
    return JsonResponse({"username": "alice", "password_hash": "hashed-secret"})


def clean_view(request: object) -> HttpResponse:
    user = User.objects.create(username="bob")
    return JsonResponse({"id": user.id, "username": user.username})


urlpatterns = [
    path("ping/", ping_view),
    path("overfetch/", overfetch_view),
    path("sensitive-leak/", sensitive_leak_view),
    path("clean/", clean_view),
]
