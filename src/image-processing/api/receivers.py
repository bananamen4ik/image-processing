"""Signal receivers."""

from typing import Any

from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

from custom_auth.models import CustomUser


@receiver(
    post_save,
    sender=CustomUser,
    weak=False,
    dispatch_uid='token_create',
)
def token_create(
    sender: type[CustomUser],
    instance: CustomUser,
    created: bool,
    **kwargs: Any,
) -> None:
    """Creates a token after a user is created."""
    if not created:
        return

    Token.objects.create(user=instance)
