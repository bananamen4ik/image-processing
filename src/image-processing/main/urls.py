"""URL configuration."""

from django.urls import path
from django.views.generic import TemplateView

app_name = 'main'
urlpatterns = [
    path('', TemplateView.as_view(template_name='main/index.html'), name='index'),
    path('plans/', TemplateView.as_view(template_name='main/plans.html'), name='plans'),
    path('about/', TemplateView.as_view(template_name='main/about.html'), name='about'),
]
