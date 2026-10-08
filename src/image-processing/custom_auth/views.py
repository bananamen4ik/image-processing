from django.views.generic import CreateView
from django.urls import (
    reverse_lazy,
    reverse,
)
from django.contrib.auth.views import (
    LoginView as BaseLoginView,
    PasswordResetView as BasePasswordResetView,
    PasswordResetDoneView as BasePasswordResetDoneView,
    PasswordResetConfirmView as BasePasswordResetConfirmView,
    PasswordResetCompleteView as BasePasswordResetCompleteView,
)
from django.http.response import HttpResponseRedirect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator

from custom_auth.forms import (
    UserCreationForm,
    AuthenticationForm,
    PasswordResetForm,
    SetPasswordForm,
)


@method_decorator(
    [sensitive_post_parameters(), never_cache],
    name='dispatch',
)
class SignupView(CreateView):
    form_class = UserCreationForm
    template_name = 'custom_auth/signup.html'
    success_url = reverse_lazy('custom_auth:login')

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse('main:index'))

        return super().dispatch(request, *args, **kwargs)


class LoginView(BaseLoginView):
    form_class = AuthenticationForm
    template_name = 'custom_auth/login.html'
    redirect_authenticated_user = True


class PasswordResetView(BasePasswordResetView):
    form_class = PasswordResetForm
    success_url = reverse_lazy('custom_auth:password_reset_done')
    template_name = 'custom_auth/password_reset.html'
    email_template_name = 'custom_auth/email/password_reset.html'
    subject_template_name = 'custom_auth/email/password_reset_subject.txt'


class PasswordResetDoneView(BasePasswordResetDoneView):
    template_name = 'custom_auth/password_reset_done.html'


class PasswordResetConfirmView(BasePasswordResetConfirmView):
    form_class = SetPasswordForm
    success_url = reverse_lazy('custom_auth:password_reset_complete')
    template_name = 'custom_auth/password_reset_confirm.html'


class PasswordResetCompleteView(BasePasswordResetCompleteView):
    template_name = 'custom_auth/password_reset_complete.html'
