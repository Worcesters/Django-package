from django.urls import include, path

urlpatterns = [
    path("api/inference/", include("inference.urls")),
]
