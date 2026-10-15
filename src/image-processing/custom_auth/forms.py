"""Provides Django authentication forms."""

from django.contrib.auth.forms import (
    AuthenticationForm as BaseAuthenticationForm,
)
from django.contrib.auth.forms import BaseUserCreationForm
from django.contrib.auth.forms import (
    PasswordResetForm as BasePasswordResetForm,
)
from django.contrib.auth.forms import (
    SetPasswordForm as BaseSetPasswordForm,
)

from common.forms import CustomTemplateFormMixin
from custom_auth.models import CustomUser


class UserCreationForm(CustomTemplateFormMixin, BaseUserCreationForm):
    """Extends the default user creation form with an email field."""

    class Meta(BaseUserCreationForm.Meta):  # ty: ignore[invalid-attribute-override]
        """Configures the model and fields used by the form."""

        model = CustomUser
        fields = BaseUserCreationForm.Meta.fields + ('email',)


class AuthenticationForm(CustomTemplateFormMixin, BaseAuthenticationForm):
    """Extends the default authentication form with Mixin."""


class PasswordResetForm(CustomTemplateFormMixin, BasePasswordResetForm):
    """Extends the default password reset form with Mixin."""


class SetPasswordForm(CustomTemplateFormMixin, BaseSetPasswordForm):
    """Extends the default set password form with Mixin."""
