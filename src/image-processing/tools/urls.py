"""URL configuration."""

from django.urls import path

from tools.views import (
    ConvertView,
    IndexView,
    OptimizeView,
    ResizeView,
)

app_name = 'tools'
urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('resize/', ResizeView.as_view(), name='resize'),
    path('convert/', ConvertView.as_view(), name='convert'),
    path('optimize/', OptimizeView.as_view(), name='optimize'),
]
