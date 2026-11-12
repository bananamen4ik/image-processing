"""A dict of all registered sitemaps."""

from custom_auth.sitemaps import CustomAuthSitemap
from main.sitemaps import MainSitemap

sitemaps = {
    'main': MainSitemap,
    'custom_auth': CustomAuthSitemap,
}
