"""URL configuration."""

from django.urls import path

from tools.views import IndexView

app_name = 'tools'
urlpatterns = [
    path('', IndexView.as_view(), name='index'),
]
