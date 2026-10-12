from django.test import TestCase
from django.urls import reverse_lazy
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.utils.translation import gettext as _

from faker import Faker

from custom_auth.models import CustomUser
from user_profile.views import PasswordChangeView


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


class PasswordChangeViewTests(TestCase):
    URI = reverse_lazy('user_profile:password_change')
    fake = Faker()

    def setUp(self):
        self.user_password = self.fake.unique.password()
        self.user = CustomUser.objects.create_user(
            username=self.fake.user_name(),
            email=self.fake.email(),
            password=self.user_password,
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

    def test_valid_change_password(self):
        self.client.login(
            username=self.user.username,
            password=self.user_password,
        )

        new_user_password = self.fake.unique.password()
        response = self.client.post(
            self.URI,
            data={
                'old_password': self.user_password,
                'new_password1': new_user_password,
                'new_password2': new_user_password,
            },
        )

        self.assertRedirects(
            response,
            PasswordChangeView.success_url,
        )

        self.client.logout()

        self.assertTrue(
            self.client.login(
                username=self.user.username,
                password=new_user_password,
            ),
        )

    def test_invalid_old_password(self):
        self.client.login(
            username=self.user.username,
            password=self.user_password,
        )

        new_user_password = self.fake.unique.password()
        response = self.client.post(
            self.URI,
            data={
                'old_password': self.fake.unique.password(),
                'new_password1': new_user_password,
                'new_password2': new_user_password,
            },
        )

        self.assertFormError(
            response.context['form'],
            'old_password',
            _('Your old password was entered incorrectly. Please enter it again.'),
        )

    def test_new_passwords_not_match(self):
        self.client.login(
            username=self.user.username,
            password=self.user_password,
        )

        response = self.client.post(
            self.URI,
            data={
                'old_password': self.user_password,
                'new_password1': self.fake.unique.password(),
                'new_password2': self.fake.unique.password(),
            },
        )

        self.assertFormError(
            response.context['form'],
            'new_password2',
            _('The two password fields didn’t match.'),
        )
