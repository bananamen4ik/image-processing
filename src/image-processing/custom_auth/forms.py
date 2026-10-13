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
    class Meta(BaseUserCreationForm.Meta):
        model = CustomUser
        fields = BaseUserCreationForm.Meta.fields + ('email',)


class AuthenticationForm(CustomTemplateFormMixin, BaseAuthenticationForm): ...


class PasswordResetForm(CustomTemplateFormMixin, BasePasswordResetForm): ...


class SetPasswordForm(CustomTemplateFormMixin, BaseSetPasswordForm): ...
