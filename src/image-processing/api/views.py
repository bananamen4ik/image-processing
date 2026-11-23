"""Views of the application."""

from collections.abc import Sequence
from typing import (
    ClassVar,
    cast,
)

from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import (
    BaseParser,
    MultiPartParser,
)
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from api.pagination import ResponsePaginationMixin
from api.serializers import (
    CreateConvertOperationRequestSerializer,
    CreateOptimizeOperationRequestSerializer,
    CreateResizeOperationRequestSerializer,
    OperationResponseSerializer,
    PaginationOperationResponseSerializer,
    ProfileRemainingOperationsResponseSerializer,
    SuccessResponseSerializer,
)
from custom_auth.models import CustomUser
from tools import tasks
from tools.forms import (
    ConvertForm,
    OptimizeForm,
    ResizeForm,
)
from tools.models import Operation
from user_profile.services import get_daily_remaining


class ProfileRemainingOperationsView(APIView):
    """Returns the number of available operations per day."""

    @extend_schema(
        description=_('Returns the number of available operations per day.'),
        tags=['profile'],
        responses=ProfileRemainingOperationsResponseSerializer,
    )
    def get(self, request: Request) -> Response:
        """Returns the number of available operations per day."""
        user = cast(CustomUser, request.user)
        serializer = ProfileRemainingOperationsResponseSerializer(
            instance={
                'remaining_operations': get_daily_remaining(user),
            },
        )

        return Response(serializer.data)


class ResizeOperationView(ResponsePaginationMixin, APIView):
    """Creates a resize operation."""

    # ty: ignore[incompatible-attribute-override]
    parser_classes: ClassVar[Sequence[type[BaseParser]]] = [MultiPartParser]

    @extend_schema(
        description=_('A list of all resize operations that have been created.'),
        tags=['tools'],
        responses=PaginationOperationResponseSerializer,
    )
    def get(self, request: Request) -> Response:
        """A list of all resize operations that have been created."""
        operations = Operation.objects.filter(
            user=request.user,
            type=Operation.Type.RESIZE,
        )
        return self.get_pagination_response(operations, OperationResponseSerializer)

    @extend_schema(
        description=_('Creates a resize operation.'),
        tags=['tools'],
        responses={
            status.HTTP_201_CREATED: SuccessResponseSerializer,
        },
        request=CreateResizeOperationRequestSerializer,
    )
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

        response = SuccessResponseSerializer(
            instance={
                'success': True,
            },
        )

        return Response(response.data, status.HTTP_201_CREATED)


class ConvertOperationView(ResponsePaginationMixin, APIView):
    """Creates a convert operation."""

    # ty: ignore[incompatible-attribute-override]
    parser_classes: ClassVar[Sequence[type[BaseParser]]] = [MultiPartParser]

    @extend_schema(
        description=_('Creates a convert operation.'),
        tags=['tools'],
        responses={
            status.HTTP_201_CREATED: SuccessResponseSerializer,
        },
        request=CreateConvertOperationRequestSerializer,
    )
    def post(self, request: Request) -> Response:
        """Creates a convert operation."""
        form = ConvertForm(
            data=request.POST,
            files=request.FILES,
            require_captcha=False,
            request=request,
        )

        if not form.is_valid():
            raise ValidationError(form.errors.get_json_data())

        form.save()

        # A countdown has been added to simulate a busy queue.
        tasks.image_convert_processing.apply_async((form.instance.pk,), countdown=5)

        return Response({'success': True}, status.HTTP_201_CREATED)

    @extend_schema(
        description=_('A list of all convert operations that have been created.'),
        tags=['tools'],
        responses=PaginationOperationResponseSerializer,
    )
    def get(self, request: Request) -> Response:
        """A list of all convert operations that have been created."""
        operations = Operation.objects.filter(
            user=request.user,
            type=Operation.Type.CONVERT,
        )
        return self.get_pagination_response(operations, OperationResponseSerializer)


class OptimizeOperationView(ResponsePaginationMixin, APIView):
    """Creates an optimize operation."""

    # ty: ignore[incompatible-attribute-override]
    parser_classes: ClassVar[Sequence[type[BaseParser]]] = [MultiPartParser]

    @extend_schema(
        description=_('Creates an optimize operation.'),
        tags=['tools'],
        responses={
            status.HTTP_201_CREATED: SuccessResponseSerializer,
        },
        request=CreateOptimizeOperationRequestSerializer,
    )
    def post(self, request: Request) -> Response:
        """Creates an optimize operation."""
        form = OptimizeForm(
            files=request.FILES,
            require_captcha=False,
            request=request,
        )

        if not form.is_valid():
            raise ValidationError(form.errors.get_json_data())

        form.save()

        # A countdown has been added to simulate a busy queue.
        tasks.image_optimize_processing.apply_async((form.instance.pk,), countdown=5)

        return Response({'success': True}, status.HTTP_201_CREATED)

    @extend_schema(
        description=_('A list of all optimize operations that have been created.'),
        tags=['tools'],
        responses=PaginationOperationResponseSerializer,
    )
    def get(self, request: Request) -> Response:
        """A list of all optimize operations that have been created."""
        operations = Operation.objects.filter(
            user=request.user,
            type=Operation.Type.OPTIMIZE,
        )
        return self.get_pagination_response(operations, OperationResponseSerializer)
