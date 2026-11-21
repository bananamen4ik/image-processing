"""URL configuration."""

from django.urls import path

from api.views import (
    ProfileRemainingOperationsView,
    ResizeOperationView,
)

app_name = 'api'
urlpatterns = [
    path(
        'profile/remaining-operations/',
        ProfileRemainingOperationsView.as_view(),
        name='profile_remaining_operations',
    ),
    path(
        'tools/resize/',
        ResizeOperationView.as_view(),
        name='tools_resize',
    ),
]
