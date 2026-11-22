"""Application serializers."""

from rest_framework import serializers

from tools.models import Operation


class ProfileRemainingOperationsSerializer(serializers.Serializer):
    """Displays the number of remaining operations for the day."""

    remaining_operations = serializers.IntegerField(read_only=True)


class OperationListSerializer(serializers.ModelSerializer):
    """A serializer for operation list."""

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
