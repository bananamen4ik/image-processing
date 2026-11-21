"""URL configuration."""

from django.urls import path

from api.views import ProfileRemainingOperationsView

app_name = 'api'
urlpatterns = [
    path(
        'profile/remaining-operations/',
        ProfileRemainingOperationsView.as_view(),
        name='profile_ramaining_operations',
    ),
]
