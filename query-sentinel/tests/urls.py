"""URLs minimales pour les tests."""

from django.contrib.auth.models import User
from django.db import connection
from django.http import HttpResponse
from django.urls import path


def ping_view(request: object) -> HttpResponse:
    return HttpResponse("ok")


def n_plus_one_view(request: object) -> HttpResponse:
    users = list(User.objects.all()[:4])
    for user in users:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 WHERE %s = %s", [user.id, user.id])
    return HttpResponse(f"users={len(users)}")


urlpatterns = [
    path("ping/", ping_view),
    path("n-plus-one/", n_plus_one_view),
]
