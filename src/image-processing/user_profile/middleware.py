"""User Profile middlewares."""

from collections.abc import Awaitable
from typing import (
    TYPE_CHECKING,
    cast,
)

from django.http import (
    HttpRequest,
    HttpResponseBase,
)
from django.utils import timezone

from custom_auth.models import CustomUser

if TYPE_CHECKING:
    from django.utils.deprecation import _AnyGetResponseCallable


class TimeZoneMiddleware:
    """Manages the time zone."""

    def __init__(self, get_response: '_AnyGetResponseCallable') -> None:
        """One-time configuration and initialization."""
        self.get_response = get_response

    def __call__(
        self,
        request: HttpRequest,
    ) -> HttpResponseBase | Awaitable[HttpResponseBase]:
        """Sets the time zone."""
        current_timezone = timezone.get_current_timezone()

        if request.user.is_authenticated:
            user = cast(CustomUser, request.user)
            current_timezone = user.user_profile.time_zone

        with timezone.override(current_timezone):
            response = self.get_response(request)

        return response
