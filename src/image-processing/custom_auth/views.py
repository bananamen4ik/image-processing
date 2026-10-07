from django.views.generic import CreateView
from django.urls import (
    reverse_lazy,
    reverse,
)
from django.contrib.auth.views import LoginView as BaseLoginView
from django.http.response import HttpResponseRedirect

from custom_auth.forms import (
    UserCreationForm,
    AuthenticationForm,
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
