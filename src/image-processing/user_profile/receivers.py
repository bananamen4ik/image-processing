"""Signal receivers."""

from typing import Any

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import get_language

from custom_auth.models import CustomUser
from user_profile.models import UserProfile


@receiver(
    post_save,
    sender=CustomUser,
    weak=False,
    dispatch_uid='user_profile_create',
)
def user_profile_create(
    sender: type[CustomUser],
    instance: CustomUser,
    created: bool,
    **kwargs: Any,
) -> None:
    """Creates a user profile after a user is created."""
    if not created:
        return

    UserProfile.objects.create(
        user=instance,
        language=get_language(),
    )
