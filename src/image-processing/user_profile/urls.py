"""URL configuration."""

from django.urls import path

from user_profile.views import (
    PasswordChangeDoneView,
    PasswordChangeView,
    ProfileEditView,
    ProfileInfoView,
    ProfileView,
)

app_name = 'user_profile'
urlpatterns = [
    path('', ProfileView.as_view(), name='index'),
    path('password-change/', PasswordChangeView.as_view(), name='password_change'),
    path(
        'password-change/done/',
        PasswordChangeDoneView.as_view(),
        name='password_change_done',
    ),
    path('info/', ProfileInfoView.as_view(), name='info'),
    path('edit/', ProfileEditView.as_view(), name='edit'),
]
