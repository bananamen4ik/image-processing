"""Tools views."""

from typing import TYPE_CHECKING

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http.response import HttpResponse
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView

from tools import tasks
from tools.forms import ResizeForm
from tools.models import Operation

if TYPE_CHECKING:
    from django.contrib.messages.views import _F


class IndexView(LoginRequiredMixin, TemplateView):
    """Displays the tool selection page."""

    template_name = 'tools/index.html'


class ResizeView(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    """Displays the resize tool page."""

    template_name = 'tools/resize.html'
    form_class = ResizeForm
    success_url = reverse_lazy('tools:resize')
    success_message = _(
        'The image has been successfully submitted for "Resize" processing.',
    )

    def form_valid(self, form: '_F') -> HttpResponse:  # ruff: ignore[UP037]
        """Before saving, it sets the required fields and runs a celery task."""
        instance: Operation = form.instance
        instance.user = self.request.user
        instance.type = Operation.Type.RESIZE
        instance.parameters = {
            'width': form.cleaned_data['width'],
            'height': form.cleaned_data['height'],
        }

        response = super().form_valid(form)

        tasks.image_resize_processing.delay(instance.pk)

        return response
