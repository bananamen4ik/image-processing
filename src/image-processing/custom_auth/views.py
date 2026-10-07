from django.views.generic import CreateView
from django.urls import reverse_lazy

from custom_auth.forms import UserCreationForm


class SignupView(CreateView):
    form_class = UserCreationForm
    template_name = 'custom_auth/signup.html'
    success_url = reverse_lazy('main:index')
