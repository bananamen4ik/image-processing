"""App Sitemaps."""

from collections.abc import Iterable

from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class MainSitemap(Sitemap):  # pragma: no cover
    """Main Sitemap."""

    changefreq = 'weekly'
    priority = 0.5

    i18n = True
    alternates = True
    x_default = True

    def items(self) -> Iterable[dict[str, str]]:
        """Returns all the page for the application."""
        return [
            {'uri_name': 'main:index'},
            {'uri_name': 'main:plans'},
            {'uri_name': 'main:about'},
        ]

    def location(self, item: dict[str, str]) -> str:
        """Returns the URI associated with the `uri_name` key."""
        return reverse(item['uri_name'])
