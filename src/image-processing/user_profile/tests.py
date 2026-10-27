"""Tests for the user profile app."""

from typing import cast

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.db.models.fields import Field
from django.test import TestCase
from django.urls import reverse_lazy
from django.utils import translation
from django.utils.translation import gettext as _
from faker import Faker

from custom_auth.models import CustomUser
from user_profile.models import UserProfile
from user_profile.views import PasswordChangeView


class ProfileViewTests(TestCase):
    """Tests the profile view."""

    URI = reverse_lazy('user_profile:index')
    fake = Faker()

    def setUp(self) -> None:
        """Sets up the user."""
        self.user = CustomUser.objects.create_user(
            username=self.fake.user_name(),
            email=self.fake.email(),
            password=self.fake.password(),
        )

    def test_accessibility(self) -> None:
        """Checking that the page is accessible."""
        response = self.client.get(self.URI)
        self.assertRedirects(
            response,
            f'{settings.LOGIN_URL}?{REDIRECT_FIELD_NAME}={self.URI}',
        )

        self.client.force_login(self.user)

        response = self.client.get(self.URI)
        self.assertEqual(response.status_code, 200)


class PasswordChangeViewTests(TestCase):
    """Tests the password change view."""

    URI = reverse_lazy('user_profile:password_change')
    fake = Faker()

    def setUp(self) -> None:
        """Sets up the user."""
        self.user_password = self.fake.unique.password()
        self.user = CustomUser.objects.create_user(
            username=self.fake.user_name(),
            email=self.fake.email(),
            password=self.user_password,
        )

    def test_accessibility(self) -> None:
        """Checking that the page is accessible."""
        response = self.client.get(self.URI)
        self.assertRedirects(
            response,
            f'{settings.LOGIN_URL}?{REDIRECT_FIELD_NAME}={self.URI}',
        )

        self.client.force_login(self.user)

        response = self.client.get(self.URI)
        self.assertEqual(response.status_code, 200)

    def test_valid_change_password(self) -> None:
        """Checks functionality using valid data."""
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
            str(PasswordChangeView.success_url),
        )

        self.client.logout()

        self.assertTrue(
            self.client.login(
                username=self.user.username,
                password=new_user_password,
            ),
        )

    def test_invalid_old_password(self) -> None:
        """Tests the logic for an incorrectly entered previous password."""
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

    def test_new_passwords_not_match(self) -> None:
        """Tests the logic for new passwords that are not equal."""
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


class PasswordChangeDoneViewTests(TestCase):
    """Tests the password change done view."""

    URI = reverse_lazy('user_profile:password_change_done')
    fake = Faker()

    def setUp(self) -> None:
        """Sets up the user."""
        self.user = CustomUser.objects.create_user(
            username=self.fake.user_name(),
            email=self.fake.email(),
            password=self.fake.password(),
        )

    def test_accessibility(self) -> None:
        """Checking that the page is accessible."""
        response = self.client.get(self.URI)
        self.assertRedirects(
            response,
            f'{settings.LOGIN_URL}?{REDIRECT_FIELD_NAME}={self.URI}',
        )

        self.client.force_login(self.user)

        response = self.client.get(self.URI)
        self.assertEqual(response.status_code, 200)


class ProfileInfoViewTests(TestCase):
    """Tests the profile info view."""

    URI = reverse_lazy('user_profile:info')
    fake = Faker()

    def setUp(self) -> None:
        """Sets up the user."""
        password = self.fake.password()
        self.user = CustomUser.objects.create_user(
            username=self.fake.user_name(),
            email=self.fake.email(),
            password=password,
        )

    def test_auth_accessibility(self) -> None:
        """Checks whether the page is accessible to an authorized user."""
        response = self.client.get(self.URI)
        self.assertRedirects(
            response,
            f'{settings.LOGIN_URL}?{REDIRECT_FIELD_NAME}={self.URI}',
        )

        self.client.force_login(self.user)

        response = self.client.get(self.URI)
        self.assertEqual(response.status_code, 200)


class ProfileEditViewTests(TestCase):
    """Tests the profile edit view."""

    URI = reverse_lazy('user_profile:edit')
    fake = Faker()

    def setUp(self) -> None:
        """Sets up the users."""
        self.user1_password = self.fake.unique.password()
        self.user1 = CustomUser.objects.create_user(
            username=self.fake.unique.user_name(),
            email=self.fake.unique.email(),
            password=self.user1_password,
        )

        self.user2_password = self.fake.unique.password()
        self.user2 = CustomUser.objects.create_user(
            username=self.fake.unique.user_name(),
            email=self.fake.unique.email(),
            password=self.user1_password,
        )

    def test_auth_accessibility(self) -> None:
        """Checks whether the page is accessible to an authorized user."""
        response = self.client.get(self.URI)
        self.assertRedirects(
            response,
            f'{settings.LOGIN_URL}?{REDIRECT_FIELD_NAME}={self.URI}',
        )

        self.client.force_login(self.user1)

        response = self.client.get(self.URI)
        self.assertEqual(response.status_code, 200)

    def test_valid_update(self) -> None:
        """Checks to see if the user data was updated successfully."""
        is_login = self.client.login(
            username=self.user1.username,
            password=self.user1_password,
        )
        self.assertTrue(is_login)

        response = self.client.get(self.URI)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['user'].username, self.user1.username)
        self.assertEqual(response.context['user'].email, self.user1.email)

        new_username = self.fake.unique.user_name()
        new_email = self.fake.unique.email()
        response = self.client.post(
            self.URI,
            data={
                'username': new_username,
                'email': new_email,
            },
        )

        self.assertRedirects(response, str(self.URI))

        self.user1.refresh_from_db()
        self.assertEqual(self.user1.username, new_username)
        self.assertEqual(self.user1.email, new_email)

    def test_username_exists_update(self) -> None:
        """Checks for errors when updating an existing username."""
        is_login = self.client.login(
            username=self.user1.username,
            password=self.user1_password,
        )
        self.assertTrue(is_login)

        response = self.client.get(self.URI)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['user'].username, self.user1.username)
        self.assertEqual(response.context['user'].email, self.user1.email)

        response = self.client.post(
            self.URI,
            data={
                'username': self.user2.username,
                'email': self.user1.email,
            },
        )
        username_field = cast(
            Field,
            CustomUser._meta.get_field(CustomUser.USERNAME_FIELD),
        )

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context['form'],
            'username',
            str(username_field.error_messages['unique']),
        )

    def test_email_exists_update(self) -> None:
        """Checks for errors when updating an existing email."""
        is_login = self.client.login(
            username=self.user1.username,
            password=self.user1_password,
        )
        self.assertTrue(is_login)

        response = self.client.get(self.URI)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['user'].username, self.user1.username)
        self.assertEqual(response.context['user'].email, self.user1.email)

        response = self.client.post(
            self.URI,
            data={
                'username': self.user1.username,
                'email': self.user2.email,
            },
        )
        email_field = cast(
            Field,
            CustomUser._meta.get_field(CustomUser.EMAIL_FIELD),
        )

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context['form'],
            'email',
            str(email_field.error_messages['unique']),
        )


class ProfileCreatePostSaveTests(TestCase):
    """Tests profile creation after the 'post save' signal."""

    fake = Faker()

    def test_post_save_receiver(self) -> None:
        """Tests profile creation after a signal."""
        current_language = 'ru' if settings.LANGUAGE_CODE == 'en' else 'en'

        with translation.override(current_language):
            user = CustomUser.objects.create_user(
                username=self.fake.user_name(),
                email=self.fake.email(),
                password=self.fake.password(),
            )

        self.assertTrue(
            UserProfile.objects.filter(
                user=user,
                language=current_language,
            ).exists(),
        )


class ProfileSettingsViewTests(TestCase):
    """Tests changes to the settings."""

    URI = reverse_lazy('user_profile:settings')
    fake = Faker()

    def setUp(self) -> None:
        """Sets up the user."""
        self.user = CustomUser.objects.create_user(
            username=self.fake.user_name(),
            email=self.fake.email(),
            password=self.fake.password(),
        )

        self.user.user_profile.language = 'en'
        self.user.user_profile.time_zone = 'UTC'
        self.user.user_profile.save(update_fields=['language', 'time_zone'])

    def test_valid_data(self) -> None:
        """Tests changes to settings using correct data."""
        language = 'ru'
        time_zone = 'Turkey'

        self.client.force_login(self.user)

        response = self.client.post(
            self.URI,
            data={
                'language': language,
                'time_zone': time_zone,
            },
        )

        self.user.user_profile.refresh_from_db()

        self.assertRedirects(response, str(self.URI))
        self.assertEqual(self.user.user_profile.language, language)
        self.assertEqual(self.user.user_profile.time_zone, time_zone)

    def test_auth_accessibility(self) -> None:
        """Checks whether the page is accessible to an authorized user."""
        response = self.client.get(self.URI)
        self.assertRedirects(
            response,
            f'{settings.LOGIN_URL}?{REDIRECT_FIELD_NAME}={self.URI}',
        )

        self.client.force_login(self.user)

        response = self.client.get(self.URI)
        self.assertEqual(response.status_code, 200)

    def test_invalid_time_zone(self) -> None:
        """Checks the validation of the 'time_zone' field."""
        time_zone = 'invalid-time_zone'
        self.client.force_login(self.user)

        response = self.client.post(
            self.URI,
            data={
                'time_zone': time_zone,
                'language': self.user.user_profile.language,
            },
        )

        self.assertFormError(
            response.context['form'],
            'time_zone',
            str(
                response.context['form']
                .fields['time_zone']
                .error_messages['invalid_choice']
                % {
                    'value': time_zone,
                },
            ),
        )

    def test_invalid_language(self) -> None:
        """Checks the validation of the 'language' field."""
        language = 'invalid-language'
        self.client.force_login(self.user)

        response = self.client.post(
            self.URI,
            data={
                'time_zone': self.user.user_profile.time_zone,
                'language': language,
            },
        )

        self.assertFormError(
            response.context['form'],
            'language',
            str(
                response.context['form']
                .fields['language']
                .error_messages['invalid_choice']
                % {
                    'value': language,
                },
            ),
        )
