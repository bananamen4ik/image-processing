"""Views of the application."""

from typing import cast

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import ProfileRemainingOperationsSerializer
from custom_auth.models import CustomUser
from user_profile.services import get_daily_remaining


class ProfileRemainingOperationsView(APIView):
    """Returns the number of available operations per day."""

    def get(self, request: Request) -> Response:
        """Returns the number of available operations per day."""
        user = cast(CustomUser, request.user)
        serializer = ProfileRemainingOperationsSerializer(
            instance={
                'remaining_operations': get_daily_remaining(user),
            },
        )

        return Response(serializer.data)
