"""Provides a user profile."""

from zoneinfo import available_timezones

from django.conf import settings
from django.db import models
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _

from custom_auth.models import CustomUser


def list_available_timezones() -> list[tuple[str, str]]:
    """Returns a list tuples of available timezones."""
    return [(tz, tz) for tz in sorted(available_timezones())]


class UserProfile(models.Model):
    """Provides user profile information."""

    class Plan(models.IntegerChoices):
        """Describes acceptable plans."""

        FREE = 0, _('Free')
        PLUS = 1, _('Plus')
        PRO = 2, _('Pro')

        @property
        def daily_operation_limit(self) -> int:
            """Returns the daily operation limit."""
            return {
                self.FREE: 10,
                self.PLUS: 30,
                self.PRO: 100,
            }[self]

        @property
        def description(self) -> str:
            """Returns a description of the plan."""
            return {
                self.FREE: gettext('For occasional image processing.'),
                self.PLUS: gettext('For regular image processing.'),
                self.PRO: gettext('For users with higher processing needs.'),
            }[self]

    @property
    def daily_operation_limit(self) -> int:
        """Returns the daily operation limit via user."""
        return UserProfile.Plan(self.plan).daily_operation_limit

    user = models.OneToOneField(
        verbose_name=_('user'),
        to=CustomUser,
        on_delete=models.CASCADE,
        related_name='user_profile',
    )

    plan = models.IntegerField(
        verbose_name=_('plan'),
        choices=Plan.choices,
        default=Plan.FREE,
    )

    last_login_ip = models.GenericIPAddressField(
        verbose_name=_('last login ip'),
        null=True,
        default=None,
        blank=True,
    )

    time_zone = models.CharField(
        verbose_name=_('time zone'),
        max_length=100,
        choices=list_available_timezones,
        default=settings.TIME_ZONE,
    )

    language = models.CharField(
        verbose_name=_('language'),
        max_length=10,
        choices=settings.LANGUAGES,
        default=settings.LANGUAGE_CODE,
    )
