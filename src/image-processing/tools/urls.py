"""URL configuration."""

from django.urls import path

from tools.views import (
    IndexView,
    ResizeView,
)

app_name = 'tools'
urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('resize/', ResizeView.as_view(), name='resize'),
]
