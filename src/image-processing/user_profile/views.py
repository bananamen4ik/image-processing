"""User profile views."""

from typing import TypeVar

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    PasswordChangeDoneView as BasePasswordChangeDoneView,
)
from django.contrib.auth.views import (
    PasswordChangeView as BasePasswordChangeView,
)
from django.contrib.messages.views import SuccessMessageMixin
from django.db import models
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import UpdateView

from custom_auth.models import CustomUser
from user_profile.forms import (
    PasswordChangeForm,
    ProfileEditForm,
    ProfileSettingsForm,
)
from user_profile.models import UserProfile

_M = TypeVar('_M', bound=models.Model)


class ProfileView(LoginRequiredMixin, TemplateView):
    """Display profile page."""

    template_name = 'user_profile/index.html'


class PasswordChangeView(BasePasswordChangeView):
    """Display password change form."""

    form_class = PasswordChangeForm
    success_url = reverse_lazy('user_profile:password_change_done')
    template_name = 'user_profile/password_change.html'


class PasswordChangeDoneView(BasePasswordChangeDoneView):
    """Displays a page with a message confirming that the password change was successful."""

    template_name = 'user_profile/password_change_done.html'


class ProfileInfoView(LoginRequiredMixin, TemplateView):
    """Display profile info page."""

    template_name = 'user_profile/info.html'


class ProfileEditView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    """Display profile edit page."""

    template_name = 'user_profile/edit.html'
    form_class = ProfileEditForm
    model = CustomUser
    success_url = reverse_lazy('user_profile:edit')
    success_message = gettext_lazy(
        'Your profile was successfully updated.',
    )

    def get_object(
        self,
        queryset: models.query.QuerySet[_M] | None = None,
    ) -> _M:
        """Retrieves the user directly from the session, not from the URL."""
        self.kwargs['pk'] = self.request.user.pk
        return super().get_object(queryset=queryset)


class ProfileSettingsView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    """Display profile settings page."""

    template_name = 'user_profile/settings.html'
    form_class = ProfileSettingsForm
    model = UserProfile
    slug_field = 'user_id'
    success_url = reverse_lazy('user_profile:settings')
    success_message = gettext_lazy(
        'Your settings was successfully updated.',
    )

    def get_object(
        self,
        queryset: models.query.QuerySet[_M] | None = None,
    ) -> _M:
        """Retrieves the user pk directly from the session, not from the URL."""
        self.kwargs['slug'] = self.request.user.pk
        return super().get_object(queryset=queryset)
