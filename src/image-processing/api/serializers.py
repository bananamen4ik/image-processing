"""Application serializers."""

from rest_framework import serializers


class ProfileRemainingOperationsSerializer(serializers.Serializer):
    """Displays the number of remaining operations for the day."""

    remaining_operations = serializers.IntegerField(read_only=True)
