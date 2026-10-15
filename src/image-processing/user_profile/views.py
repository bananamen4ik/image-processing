"""User profile views."""

from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (
    PasswordChangeDoneView as BasePasswordChangeDoneView,
)
from django.contrib.auth.views import (
    PasswordChangeView as BasePasswordChangeView,
)
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from user_profile.forms import PasswordChangeForm


@method_decorator(login_required, name='dispatch')
class ProfileView(TemplateView):
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
