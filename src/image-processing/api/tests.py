"""Application Tests."""

from django.test import TestCase
from django.urls import reverse_lazy
from faker import Faker
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from api.serializers import ProfileRemainingOperationsSerializer
from custom_auth.models import CustomUser


class TokenCreatePostSaveTests(TestCase):
    """Tests the creation of a token for the user after a signal."""

    fake = Faker()

    def setUp(self) -> None:
        """Creates a user."""
        self.user = CustomUser.objects.create_user(
            username=self.fake.user_name(),
            email=self.fake.email(),
            password=self.fake.password(),
        )

    def test_create_token(self) -> None:
        """Tests token creation."""
        token = Token.objects.get(user=self.user)

        self.assertEqual(token.user, self.user)


class ProfileRemainingOperationsViewTests(APITestCase):
    """Tests the profile remaining operations view."""

    fake = Faker()
    URI = reverse_lazy('api:profile_ramaining_operations')

    def setUp(self) -> None:
        """Creates a user."""
        self.user = CustomUser.objects.create_user(
            username=self.fake.user_name(),
            email=self.fake.email(),
            password=self.fake.password(),
        )

    def test_get(self) -> None:
        """Tests get view method."""
        self.client.force_authenticate(user=self.user, token=self.user.auth_token)

        serializer = ProfileRemainingOperationsSerializer(
            instance={
                'remaining_operations': self.user.user_profile.daily_operation_limit,
            },
        )

        self.assertEqual(self.client.get(self.URI).data, serializer.data)
