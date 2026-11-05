"""User profile views."""

from datetime import timedelta
from typing import (
    Any,
    TypeVar,
    cast,
)

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    PasswordChangeDoneView as BasePasswordChangeDoneView,
)
from django.contrib.auth.views import (
    PasswordChangeView as BasePasswordChangeView,
)
from django.contrib.messages.views import SuccessMessageMixin
from django.db import models
from django.http.request import HttpRequest
from django.http.response import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import UpdateView

from custom_auth.models import CustomUser
from tools.models import Operation
from user_profile.forms import (
    PasswordChangeForm,
    ProfileChangePlanForm,
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


class ProfileUsageView(LoginRequiredMixin, TemplateView):
    """Display profile usage page."""

    template_name = 'user_profile/usage.html'
    redirect_url = reverse_lazy('user_profile:usage')

    def post(
        self,
        request: HttpRequest,
        *args: Any,
        **kwargs: Any,
    ) -> HttpResponseRedirect:
        """Changes the user's rate plan."""
        user = cast(CustomUser, self.request.user)
        change_plan_form = ProfileChangePlanForm(
            request.POST,
            instance=user.user_profile,
        )

        if change_plan_form.is_valid():
            change_plan_form.save()

        return HttpResponseRedirect(self.redirect_url)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Adds additional data to the template."""
        context = super().get_context_data(**kwargs)

        user = cast(CustomUser, self.request.user)
        user_profile = user.user_profile

        now = timezone.now()
        current_plan_title = user_profile.get_plan_display
        daily_limit = user_profile.daily_operation_limit

        daily_used = Operation.objects.filter(
            user=user,
            created_at__gte=(now - timedelta(days=1)),
            status=Operation.Status.COMPLETED,
        ).count()

        daily_remaining = daily_limit - daily_used

        plans = (
            {
                'id': plan_id,
                'title': plan_title,
                'description': UserProfile.Plan(plan_id).description,
                'daily_limit': UserProfile.Plan(plan_id).daily_operation_limit,
            }
            for plan_id, plan_title in UserProfile.Plan.choices
        )

        daily_usage_percent = min(
            round(daily_used / daily_limit * 100),
            100,
        )

        operations_stats = (
            Operation.objects.filter(
                user=user,
                status=Operation.Status.COMPLETED,
            )
            .values(
                'type',
            )
            .annotate(
                total=models.Count('id'),
            )
            .all()
        )

        types_operations_total = {
            operation_id: {
                'title': operation_title,
                'total': next(
                    (
                        operation_stats['total']
                        for operation_stats in operations_stats
                        if operation_stats['type'] == operation_id
                    ),
                    0,
                ),
            }
            for operation_id, operation_title in Operation.Type.choices
        }

        context.update(
            {
                'user_profile': user_profile,
                'current_plan_title': current_plan_title,
                'daily_limit': daily_limit,
                'daily_used': daily_used,
                'daily_remaining': daily_remaining,
                'plans': plans,
                'daily_usage_percent': daily_usage_percent,
                'types_operations_total': types_operations_total,
                'operation_type': Operation.Type,
            },
        )

        return context
