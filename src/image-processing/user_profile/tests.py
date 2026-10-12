from django.test import TestCase
from django.urls import reverse_lazy
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME

from faker import Faker

from custom_auth.models import CustomUser


class ProfileViewTests(TestCase):
    URI = reverse_lazy('user_profile:index')
    fake = Faker()

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username=self.fake.user_name(),
            email=self.fake.email(),
            password=self.fake.password(),
        )

    def test_accessibility(self):
        response = self.client.get(self.URI)
        self.assertRedirects(
            response,
            f'{settings.LOGIN_URL}?{REDIRECT_FIELD_NAME}={self.URI}',
        )

        self.client.force_login(self.user)

        response = self.client.get(self.URI)
        self.assertEqual(response.status_code, 200)
