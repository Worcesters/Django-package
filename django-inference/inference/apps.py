from django.apps import AppConfig


class InferenceConfig(AppConfig):
    """Configuration Django pour le package inference."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "inference"
    verbose_name = "Inference"