"""Basic views."""

from django.views.generic import TemplateView


class RobotsView(TemplateView):
    """Generates a robots.txt file."""

    content_type = 'text/plain'
    template_name = 'common/robots.html'
