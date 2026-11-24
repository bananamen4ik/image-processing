"""Application pagination."""

from collections.abc import Sequence
from typing import (
    TYPE_CHECKING,
)

from rest_framework.exceptions import APIException
from rest_framework.pagination import CursorPagination as BaseCursorPagination
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer
from rest_framework.settings import api_settings

if TYPE_CHECKING:
    from django.db.models.query import QuerySet
    from rest_framework.pagination import (
        _Model,
        _Row,
    )


class CursorPagination(BaseCursorPagination):
    """Ordering by pk DESC."""

    ordering = '-pk'


class ResponsePaginationMixin:
    """Pagination support for the APIView subclass."""

    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS

    def get_pagination_response(
        self,
        queryset: 'QuerySet[_Model, _Row] | Sequence[_Row]',
        serializer_class: type[BaseSerializer],
    ) -> Response:
        """Returns a response with pagination."""
        if not self.pagination_class:  # pragma: no cover
            raise APIException

        paginator = self.pagination_class()
        # ty: ignore[invalid-argument-type]
        page = paginator.paginate_queryset(queryset, self.request, self)

        serializer = serializer_class(
            page,
            many=True,
            context={'request': self.request},
        )
        return paginator.get_paginated_response(serializer.data)
