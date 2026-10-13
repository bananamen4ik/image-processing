import re

from django.conf import settings
from django.contrib.auth.password_validation import (
    MinimumLengthValidator,
    get_default_password_validators,
)
from django.contrib.sites.shortcuts import get_current_site
from django.core import mail
from django.template import loader
from django.test import TestCase
from django.urls import (
    reverse,
    reverse_lazy,
)
from django.utils.translation import (
    gettext as _,
)
from django.utils.translation import ngettext
from faker import Faker

from custom_auth.models import (
    CustomUser,
    CustomUserManager,
)
from custom_auth.views import (
    PasswordResetConfirmView,
    PasswordResetView,
    SignupView,
)


class SignupViewTests(TestCase):
    URI = reverse_lazy('custom_auth:signup')
    fake = Faker()

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username=self.fake.unique.user_name(),
            email=self.fake.unique.email(),
            password=self.fake.password(),
        )

    def test_valid_data(self):
        username = self.fake.unique.user_name()
        email = self.fake.unique.email()
        password = self.fake.password()

        response = self.client.post(
            self.URI,
            data={
                'username': username,
                'email': email,
                'password1': password,
                'password2': password,
            },
        )

        self.assertRedirects(response, SignupView.success_url)

        logged_in = self.client.login(
            username=username,
            password=password,
        )
        user = CustomUser.objects.get(username=username)

        self.assertTrue(logged_in)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_active)

    def test_user_redirect(self):
        response = self.client.get(self.URI)
        self.assertEqual(response.status_code, 200)

        self.client.force_login(self.user)

        response = self.client.get(self.URI)
        self.assertRedirects(response, reverse('main:index'))

    def test_username_exists(self):
        password = self.fake.password()
        response = self.client.post(
            self.URI,
            data={
                'username': self.user.username,
                'email': self.fake.unique.email(),
                'password1': password,
                'password2': password,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context['form'],
            'username',
            _('A user with that username already exists.'),
        )

    def test_email_exists(self):
        password = self.fake.password()
        response = self.client.post(
            self.URI,
            data={
                'username': self.fake.unique.user_name(),
                'email': self.user.email,
                'password1': password,
                'password2': password,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context['form'],
            'email',
            _('A user with that email already exists.'),
        )

    def test_password_mismatch(self):
        response = self.client.post(
            self.URI,
            data={
                'username': self.fake.unique.user_name(),
                'email': self.fake.unique.email(),
                'password1': self.fake.unique.password(),
                'password2': self.fake.unique.password(),
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context['form'],
            'password2',
            _('The two password fields didn’t match.'),
        )

    def test_username_email_normalize(self):
        username = self.fake.unique.user_name().upper()
        email = self.fake.unique.email().upper()
        password = self.fake.password()

        self.client.post(
            self.URI,
            data={
                'username': username,
                'email': email,
                'password1': password,
                'password2': password,
            },
        )

        with self.assertRaises(CustomUser.DoesNotExist):
            CustomUser.objects.get(username=username)

        user = CustomUser.objects.get(username=username.lower())

        self.assertEqual(user.username, username.lower())
        self.assertEqual(user.email, email.lower())

    def test_invalid_username(self):
        username = '$invalid-username$'
        email = self.fake.unique.email()
        password = self.fake.password()

        response = self.client.post(
            self.URI,
            data={
                'username': username,
                'email': email,
                'password1': password,
                'password2': password,
            },
        )

        self.assertFormError(
            response.context['form'],
            'username',
            _(
                'Enter a valid username. This value may contain only letters, '
                'numbers, and @/./+/-/_ characters.'
            ),
        )

    def test_invalid_email(self):
        username = self.fake.unique.user_name()
        email = 'invalid-email'
        password = self.fake.password()

        response = self.client.post(
            self.URI,
            data={
                'username': username,
                'email': email,
                'password1': password,
                'password2': password,
            },
        )

        self.assertFormError(
            response.context['form'],
            'email',
            _('Enter a valid email address.'),
        )

    def test_invalid_password_similarity(self):
        username = self.fake.unique.user_name()
        email = self.fake.unique.email()
        password = username

        response = self.client.post(
            self.URI,
            data={
                'username': username,
                'email': email,
                'password1': password,
                'password2': password,
            },
        )

        self.assertIn(
            _('The password is too similar to the %(verbose_name)s.') % {
                'verbose_name': str(CustomUser._meta.get_field('username').verbose_name),
            },
            response.context['form'].errors['password2'],
        )

    def test_invalid_password_min_length(self):
        validator = next(
            validator
            for validator in get_default_password_validators()
            if isinstance(validator, MinimumLengthValidator)
        )
        username = self.fake.unique.user_name()
        email = self.fake.unique.email()
        password = 'x' * (validator.min_length - 1)

        response = self.client.post(
            self.URI,
            data={
                'username': username,
                'email': email,
                'password1': password,
                'password2': password,
            },
        )

        self.assertIn(
            ngettext(
                'This password is too short. It must contain at least %d character.',
                'This password is too short. It must contain at least %d characters.',
                validator.min_length,
            )
            % validator.min_length,
            response.context['form'].errors['password2'],
        )

    def test_invalid_password_common(self):
        username = self.fake.unique.user_name()
        email = self.fake.unique.email()
        password = 'qwerty'

        response = self.client.post(
            self.URI,
            data={
                'username': username,
                'email': email,
                'password1': password,
                'password2': password,
            },
        )

        self.assertIn(
            _('This password is too common.'),
            response.context['form'].errors['password2'],
        )

    def test_invalid_password_numeric(self):
        username = self.fake.unique.user_name()
        email = self.fake.unique.email()
        password = '1234567890'

        response = self.client.post(
            self.URI,
            data={
                'username': username,
                'email': email,
                'password1': password,
                'password2': password,
            },
        )

        self.assertIn(
            _('This password is entirely numeric.'),
            response.context['form'].errors['password2'],
        )


class LoginViewTests(TestCase):
    URI = reverse_lazy('custom_auth:login')
    fake = Faker()

    def setUp(self):
        self.user_password = self.fake.password()
        self.user = CustomUser.objects.create_user(
            username=self.fake.unique.user_name(),
            email=self.fake.unique.email(),
            password=self.user_password,
        )

    def test_valid_login(self):
        response = self.client.post(
            self.URI,
            data={
                'username': self.user.username,
                'password': self.user_password,
            },
        )

        self.assertRedirects(response, settings.LOGIN_REDIRECT_URL)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_invalid_login(self):
        response = self.client.post(
            self.URI,
            data={
                'username': self.fake.unique.user_name(),
                'password': self.fake.password(),
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context['form'],
            None,
            _(
                'Please enter a correct %(username)s and password. Note that both '
                'fields may be case-sensitive.',
            ) % {
                'username': str(CustomUser._meta.get_field(CustomUser.USERNAME_FIELD).verbose_name),
            },
        )

    def test_not_active_login(self):
        self.user.is_active = False
        self.user.save()

        response = self.client.post(
            self.URI,
            data={
                'username': self.user.username,
                'password': self.user_password,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context['form'],
            None,
            _(
                'Please enter a correct %(username)s and password. Note that both '
                'fields may be case-sensitive.',
            ) % {
                'username': str(CustomUser._meta.get_field(CustomUser.USERNAME_FIELD).verbose_name),
            },
        )

    def test_user_redirect(self):
        response = self.client.get(self.URI)
        self.assertEqual(response.status_code, 200)

        self.client.force_login(self.user)

        response = self.client.get(self.URI)
        self.assertRedirects(response, settings.LOGIN_REDIRECT_URL)


class LogoutViewTests(TestCase):
    URI = reverse_lazy('custom_auth:logout')
    fake = Faker()

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username=self.fake.unique.user_name(),
            email=self.fake.unique.email(),
            password=self.fake.password(),
        )

    def test_get_method_not_allowed(self):
        response = self.client.get(self.URI)
        self.assertEqual(response.status_code, 405)

    def test_anonymous_user(self):
        response = self.client.post(self.URI)
        self.assertRedirects(
            response,
            settings.LOGOUT_REDIRECT_URL,
        )

    def test_valid_user(self):
        response = self.client.get(self.URI)
        self.assertTrue(not response.wsgi_request.user.is_authenticated)

        self.client.force_login(self.user)

        response = self.client.get(self.URI)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

        response = self.client.post(self.URI)
        self.assertRedirects(
            response,
            settings.LOGOUT_REDIRECT_URL,
        )
        self.assertTrue(not response.wsgi_request.user.is_authenticated)


class PasswordResetViewTests(TestCase):
    URI = reverse_lazy('custom_auth:password_reset')
    fake = Faker()

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username=self.fake.unique.user_name(),
            email=self.fake.unique.email(),
            password=self.fake.password(),
        )

    def test_invalid_email(self):
        response = self.client.post(
            self.URI,
            data={
                'email': 'invalid-email',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context['form'],
            'email',
            _('Enter a valid email address.'),
        )

    def test_user_not_active(self):
        self.user.is_active = False
        self.user.save()

        response = self.client.post(
            self.URI,
            data={
                'email': self.user.email,
            },
        )

        self.assertRedirects(
            response,
            PasswordResetView.success_url,
        )
        self.assertEqual(len(mail.outbox), 0)

    def test_valid_reset(self):
        response = self.client.post(
            self.URI,
            data={
                'email': self.user.email,
            },
        )

        subject_template_name = PasswordResetView.subject_template_name
        current_site = get_current_site(response.wsgi_request)
        context = {
            'site_name': current_site.name,
        }
        subject = loader.render_to_string(subject_template_name, context).strip()

        self.assertRedirects(
            response,
            PasswordResetView.success_url,
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, subject)
        self.assertEqual(len(mail.outbox[0].to), 1)
        self.assertIn(
            self.user.email,
            mail.outbox[0].to,
        )


class PasswordResetDoneViewTests(TestCase):
    def test_accessibility(self):
        response = self.client.get(reverse('custom_auth:password_reset_done'))
        self.assertEqual(response.status_code, 200)


class PasswordResetConfirmViewTests(TestCase):
    fake = Faker()

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username=self.fake.unique.user_name(),
            email=self.fake.unique.email(),
            password=self.fake.password(),
        )

    def test_valid_reset(self):
        reset_url_token = PasswordResetConfirmView.reset_url_token

        self.client.post(
            reverse('custom_auth:password_reset'),
            data={
                'email': self.user.email,
            },
        )

        email_body = str(mail.outbox[0].body)
        match_link = re.search(
            r'accounts/reset/([^/]+)/([^/]+)/',
            email_body,
        )

        self.assertIsNotNone(match_link)

        # noinspection unresolved-references
        uidb64, token = match_link.groups()
        uri_confirm = reverse(
            'custom_auth:password_reset_confirm',
            kwargs={
                'uidb64': uidb64,
                'token': token,
            },
        )

        response = self.client.get(uri_confirm)
        response_uri = reverse(
            'custom_auth:password_reset_confirm',
            kwargs={
                'uidb64': uidb64,
                'token': reset_url_token,
            },
        )

        self.assertRedirects(
            response,
            response_uri,
        )

        new_password = self.fake.password()
        response = self.client.post(
            response_uri,
            data={
                'new_password1': new_password,
                'new_password2': new_password,
            },
        )

        self.assertRedirects(
            response,
            PasswordResetConfirmView.success_url,
        )

        self.assertTrue(
            self.client.login(
                username=self.user.username,
                password=new_password,
            ),
        )

    def test_invalid_reset(self):
        uri_confirm = reverse(
            'custom_auth:password_reset_confirm',
            kwargs={
                'uidb64': 'invalid-uidb64',
                'token': 'invalid-token',
            },
        )

        response = self.client.get(uri_confirm)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['title'],
            _('Password reset unsuccessful'),
        )


class PasswordResetCompleteTests(TestCase):
    def test_accessibility(self):
        response = self.client.get(reverse('custom_auth:password_reset_complete'))
        self.assertEqual(response.status_code, 200)


class CustomUserTests(TestCase):
    fake = Faker()

    def test_clean(self):
        username = self.fake.user_name().upper()
        email = self.fake.email().upper()
        user = CustomUser(
            username=username,
            email=email,
        )

        user.clean()

        self.assertEqual(user.username, username.lower())
        self.assertEqual(user.email, email.lower())

    def test_normalize_username(self):
        username = self.fake.user_name().upper()
        self.assertEqual(CustomUser.normalize_username(username), username.lower())


class CustomUserManagerTests(TestCase):
    fake = Faker()

    def test_normalize_email(self):
        email = self.fake.email().upper()
        self.assertEqual(CustomUserManager.normalize_email(email), email.lower())

    def create_user_and_login(self, is_superuser=False):
        username = self.fake.user_name()
        email = self.fake.email()
        password = self.fake.password()

        create_user = (
            CustomUser.objects.create_user
            if not is_superuser
            else CustomUser.objects.create_superuser
        )

        user = create_user(
            username=username.upper(),
            email=email.upper(),
            password=password,
        )

        self.assertTrue(
            CustomUser.objects.filter(
                username=username,
                email=email,
            ).exists()
        )

        self.assertTrue(self.client.login(
            username=username,
            password=password,
        ))

        self.assertTrue(user.is_active)

        return user

    def test_create_user(self):
        user = self.create_user_and_login()

        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        user = self.create_user_and_login(is_superuser=True)

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
