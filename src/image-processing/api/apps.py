"""Application configuration."""

from django.apps import AppConfig


class ApiConfig(AppConfig):
    """Configures the application."""

    name = 'api'

    def ready(self) -> None:
        """Connects additional components after the application is ready."""
        import api.receivers  # ruff: ignore[F401]
