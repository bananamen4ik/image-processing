"""Provides business logic for user profile management."""

from datetime import timedelta

from django.utils import timezone

from custom_auth.models import CustomUser
from tools.models import Operation


def get_daily_used(user: CustomUser) -> int:
    """Returns the number of operations performed over the past day."""
    now = timezone.now()

    return Operation.objects.filter(
        user=user,
        created_at__gte=(now - timedelta(days=1)),
        status__in=(
            Operation.Status.CREATED,
            Operation.Status.PROCESSING,
            Operation.Status.COMPLETED,
        ),
    ).count()


def check_daily_used_limit(user: CustomUser) -> bool:
    """Checks the remaining daily limit.

    True if the remaining amount is greater than 0.
    """
    daily_used = get_daily_used(user)
    return (user.user_profile.daily_operation_limit - daily_used) > 0
