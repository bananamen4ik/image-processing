from django.contrib.auth.forms import (
    PasswordChangeForm as BasePasswordChangeForm,
)

from common.forms import CustomTemplateFormMixin


class PasswordChangeForm(CustomTemplateFormMixin, BasePasswordChangeForm):
    ...
