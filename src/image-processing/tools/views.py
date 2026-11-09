"""Tools views."""

from typing import (
    TYPE_CHECKING,
    Any,
    cast,
)

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView
from django.views.generic.list import MultipleObjectMixin
from PIL import Image

from custom_auth.models import CustomUser
from tools import tasks
from tools.forms import (
    ConvertForm,
    OptimizeForm,
    ResizeForm,
)
from tools.models import Operation
from user_profile.services import check_daily_used_limit

if TYPE_CHECKING:
    from django.contrib.messages.views import _F
    from django.core.paginator import _SupportsPagination
    from django.db.models.query import QuerySet
    from django.utils.functional import _StrPromise
    from django.views.generic.list import _M


class PreOrderMixin:
    """Pre-order verification."""

    pre_order_error_message = _(
        'You have reached your daily limit. Please wait or upgrade your plan.',
    )

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """Checks the remaining daily limit according to the plan.

        Use only after LoginRequiredMixin.
        """
        user = cast(CustomUser, request.user)
        can_order = check_daily_used_limit(user)

        if not can_order:
            self.object = None
            form = self.get_form()
            form.add_error(
                None,
                self.pre_order_error_message,
            )
            return self.form_invalid(form)
        return super().post(request, *args, **kwargs)


class IndexView(LoginRequiredMixin, TemplateView):
    """Displays the tool selection page."""

    template_name = 'tools/index.html'


class BaseOperationView(
    LoginRequiredMixin,
    PreOrderMixin,
    MultipleObjectMixin,
    SuccessMessageMixin,
    CreateView,
):  # ty: ignore[invalid-attribute-override, invalid-method-override]
    """A base class that describes view operation.

    Not intended for direct use!
    """

    ordering = '-pk'
    paginate_by = 6

    current_url: '_StrPromise'
    title: '_StrPromise'
    description: '_StrPromise'
    button_title: '_StrPromise'

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """Adds operations for history and pagination."""
        self.object_list = self.get_queryset()
        return super().post(request, *args, **kwargs)

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """Adds operations for history and pagination."""
        self.object_list = self.get_queryset()
        return super().get(request, *args, **kwargs)

    def get_context_data(
        self,
        *,
        object_list: '_SupportsPagination[_M] | None' = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Adds convenient pagination for display in the template."""
        context = super().get_context_data(object_list=object_list, **kwargs)

        paginator: Paginator | None = context.get('paginator')
        if paginator is not None:  # pragma: no cover
            context['paginator_elided'] = paginator.get_elided_page_range(
                number=context['page_obj'].number,
                on_each_side=1,
            )

        context['page_kwarg'] = self.page_kwarg
        context['url'] = self.current_url
        context['title'] = self.title
        context['description'] = self.description
        context['button_title'] = self.button_title

        return context


class ResizeView(BaseOperationView):
    """Displays the resize tool page."""

    template_name = 'tools/resize.html'
    form_class = ResizeForm
    success_url = reverse_lazy('tools:resize')
    success_message = _(
        'The image has been successfully submitted for "Resize" processing.',
    )

    current_url = reverse_lazy('tools:resize')
    title = _('Resize')
    description = _('Resize your images to the dimensions you need.')
    button_title = _('Resize image')

    def get_queryset(self) -> 'QuerySet[_M]':
        """Displays only its own images of a specific type."""
        self.queryset = Operation.objects.filter(
            user=self.request.user,
            type=Operation.Type.RESIZE,
        )
        return super().get_queryset()

    def form_valid(self, form: '_F') -> HttpResponse:
        """Before saving, it sets the required fields and runs a celery task."""
        instance: Operation = form.instance
        instance.user = self.request.user
        instance.type = Operation.Type.RESIZE
        instance.parameters = {
            'width': form.cleaned_data['width'],
            'height': form.cleaned_data['height'],
        }

        response = super().form_valid(form)

        # A countdown has been added to simulate a busy queue.
        tasks.image_resize_processing.apply_async((instance.pk,), countdown=5)
        return response


class ConvertView(BaseOperationView):
    """Displays the convert tool page."""

    template_name = 'tools/convert.html'
    form_class = ConvertForm
    success_url = reverse_lazy('tools:convert')
    success_message = _(
        'The image has been successfully submitted for "Convert" processing.',
    )

    current_url = reverse_lazy('tools:convert')
    title = _('Convert')
    description = _('Convert images between supported formats.')
    button_title = _('Convert image')

    def get_queryset(self) -> 'QuerySet[_M]':
        """Displays only its own images of a specific type."""
        self.queryset = Operation.objects.filter(
            user=self.request.user,
            type=Operation.Type.CONVERT,
        )
        return super().get_queryset()

    def form_valid(self, form: '_F') -> HttpResponse:
        """Before saving, it sets the required fields and runs a celery task."""
        instance: Operation = form.instance
        instance.user = self.request.user
        instance.type = Operation.Type.CONVERT

        extension = form.cleaned_data['extension']
        pil_format = Image.registered_extensions()[extension]
        instance.parameters = {
            'extension': extension,
            'format': pil_format,
        }

        response = super().form_valid(form)

        # A countdown has been added to simulate a busy queue.
        tasks.image_convert_processing.apply_async((instance.pk,), countdown=5)
        return response


class OptimizeView(BaseOperationView):
    """Displays the optimize tool page."""

    template_name = 'tools/optimize.html'
    form_class = OptimizeForm
    success_url = reverse_lazy('tools:optimize')
    success_message = _(
        'The image has been successfully submitted for "Optimize" processing.',
    )

    current_url = reverse_lazy('tools:optimize')
    title = _('Optimize')
    description = _('Reduce image size while maintaining good quality.')
    button_title = _('Optimize image')

    def get_queryset(self) -> 'QuerySet[_M]':
        """Displays only its own images of a specific type."""
        self.queryset = Operation.objects.filter(
            user=self.request.user,
            type=Operation.Type.OPTIMIZE,
        )
        return super().get_queryset()

    def form_valid(self, form: '_F') -> HttpResponse:
        """Before saving, it sets the required fields and runs a celery task."""
        instance: Operation = form.instance
        instance.user = self.request.user
        instance.type = Operation.Type.OPTIMIZE
        instance.parameters = {}

        response = super().form_valid(form)

        # A countdown has been added to simulate a busy queue.
        tasks.image_optimize_processing.apply_async((instance.pk,), countdown=5)
        return response
