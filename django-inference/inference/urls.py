from django.urls import path

from . import views

app_name = "inference"

urlpatterns = [
    path("health/", views.InferenceHealthView.as_view(), name="health"),
]