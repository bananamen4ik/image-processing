"""Signal receivers."""

from typing import Any

from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import HttpRequest
from django.utils.translation import get_language

from common.services import get_ip
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


@receiver(
    user_logged_in,
    sender=CustomUser,
    weak=False,
    dispatch_uid='user_profile_set_last_login_ip',
)
def user_profile_set_last_login_ip(
    sender: type[CustomUser],
    request: HttpRequest,
    user: CustomUser,
    **kwargs: Any,
) -> None:
    """Sets the IP address after successful authentication."""
    user.user_profile.last_login_ip = get_ip(request)
    user.user_profile.save(update_fields=['last_login_ip'])
