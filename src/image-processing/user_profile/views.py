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
    template_name = 'user_profile/index.html'


class PasswordChangeView(BasePasswordChangeView):
    form_class = PasswordChangeForm
    success_url = reverse_lazy('user_profile:password_change_done')
    template_name = 'user_profile/password_change.html'


class PasswordChangeDoneView(BasePasswordChangeDoneView):
    template_name = 'user_profile/password_change_done.html'
