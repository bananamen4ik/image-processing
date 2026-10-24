"""Application configuration."""

from django.apps import AppConfig


class UserProfileConfig(AppConfig):
    """Configures the application."""

    name = 'user_profile'

    def ready(self) -> None:
        """Connects additional components after the application is ready."""
