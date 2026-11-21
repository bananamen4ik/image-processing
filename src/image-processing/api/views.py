"""Views of the application."""

from collections.abc import Sequence
from typing import (
    ClassVar,
    cast,
)

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import (
    BaseParser,
    MultiPartParser,
)
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import ProfileRemainingOperationsSerializer
from custom_auth.models import CustomUser
from tools import tasks
from tools.forms import ResizeForm
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


class ResizeOperationView(APIView):
    """Creates a resize operation."""

    # ty: ignore[incompatible-attribute-override]
    parser_classes: ClassVar[Sequence[type[BaseParser]]] = [MultiPartParser]

    def post(self, request: Request) -> Response:
        """Creates a resize operation."""
        form = ResizeForm(
            data=request.POST,
            files=request.FILES,
            require_captcha=False,
            request=request,
        )

        if not form.is_valid():
            raise ValidationError(form.errors.get_json_data())

        form.save()

        # A countdown has been added to simulate a busy queue.
        tasks.image_resize_processing.apply_async((form.instance.pk,), countdown=5)

        return Response({'success': True}, status.HTTP_201_CREATED)
