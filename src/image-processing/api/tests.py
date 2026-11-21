"""Application Tests."""

from django.test import TestCase
from faker import Faker
from rest_framework.authtoken.models import Token

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
