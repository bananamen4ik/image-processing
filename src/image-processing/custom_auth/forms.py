from django.contrib.auth.forms import (
    BaseUserCreationForm,
    AuthenticationForm as BaseAuthenticationForm,
    PasswordResetForm as BasePasswordResetForm,
    SetPasswordForm as BaseSetPasswordForm,
)

from custom_auth.models import CustomUser
from common.forms import CustomTemplateFormMixin


class UserCreationForm(CustomTemplateFormMixin, BaseUserCreationForm):
    class Meta(BaseUserCreationForm.Meta):
        model = CustomUser
        fields = BaseUserCreationForm.Meta.fields + ('email',)


class AuthenticationForm(CustomTemplateFormMixin, BaseAuthenticationForm):
    ...


class PasswordResetForm(CustomTemplateFormMixin, BasePasswordResetForm):
    ...


class SetPasswordForm(CustomTemplateFormMixin, BaseSetPasswordForm):
    ...
