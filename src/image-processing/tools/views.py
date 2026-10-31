"""Tools views."""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class IndexView(LoginRequiredMixin, TemplateView):
    """Displays the tool selection page."""

    template_name = 'tools/index.html'
