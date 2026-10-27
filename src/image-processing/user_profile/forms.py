"""Provides user profile forms."""

from django.contrib.auth.forms import (
    PasswordChangeForm as BasePasswordChangeForm,
)
from django.forms import ModelForm

from common.forms import CustomTemplateFormMixin
from custom_auth.models import CustomUser
from user_profile.models import UserProfile


class PasswordChangeForm(CustomTemplateFormMixin, BasePasswordChangeForm):
    """Extends the default password change form with Mixin."""


class ProfileEditForm(CustomTemplateFormMixin, ModelForm):
    """A form that allows users to edit their personal information."""

    class Meta:
        """Configures the model and fields used by the form."""

        model = CustomUser
        fields = ('username', 'email')


class ProfileSettingsForm(CustomTemplateFormMixin, ModelForm):
    """A form that allows users to edit their settings."""

    class Meta:
        """Configures the model and fields used by the form."""

        model = UserProfile
        fields = ('time_zone', 'language')
