"""Application serializers."""

from rest_framework import serializers

from tools.forms import registered_extensions
from tools.models import Operation


class ProfileRemainingOperationsResponseSerializer(serializers.Serializer):
    """Displays the number of remaining operations for the day."""

    remaining_operations = serializers.IntegerField()


class OperationResponseSerializer(serializers.ModelSerializer):
    """A serializer for operation list."""

    parameters = serializers.DictField()

    class Meta:  # ty: ignore[incompatible-attribute-override]
        """ModelSerializer Configuration."""

        model = Operation
        fields = (
            'id',
            'uploaded_image',
            'processed_image',
            'parameters',
            'status',
            'created_at',
            'processed_at',
        )
        read_only_fields = (
            'processed_image',
            'processed_at',
            'status',
        )


class PaginationOperationResponseSerializer(serializers.Serializer):
    """Pagination Serializer in conjunction with OperationList."""

    next = serializers.URLField(allow_null=True)
    previous = serializers.URLField(allow_null=True)
    results = OperationResponseSerializer(many=True)


class SuccessResponseSerializer(serializers.Serializer):
    """Success status serializer."""

    success = serializers.BooleanField()


class CreateResizeOperationRequestSerializer(serializers.ModelSerializer):
    """A serializer for creating resize operations."""

    width = serializers.IntegerField(min_value=1, max_value=10_000)
    height = serializers.IntegerField(min_value=1, max_value=10_000)

    class Meta:  # ty: ignore[incompatible-attribute-override]
        """ModelSerializer Configuration."""

        model = Operation
        fields = (
            'uploaded_image',
            'width',
            'height',
        )


class CreateConvertOperationRequestSerializer(serializers.ModelSerializer):
    """A serializer for creating convert operations."""

    extension = serializers.ChoiceField(choices=registered_extensions())

    class Meta:  # ty: ignore[incompatible-attribute-override]
        """ModelSerializer Configuration."""

        model = Operation
        fields = (
            'uploaded_image',
            'extension',
        )


class CreateOptimizeOperationRequestSerializer(serializers.ModelSerializer):
    """A serializer for creating convert operations."""

    class Meta:  # ty: ignore[incompatible-attribute-override]
        """ModelSerializer Configuration."""

        model = Operation
        fields = ('uploaded_image',)
