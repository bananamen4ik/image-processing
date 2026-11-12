"""URL configuration for image_processing project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/

Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import (
    URLPattern,
    URLResolver,
    include,
    path,
)

from common.views import RobotsView
from image_processing.sitemaps import sitemaps

urlpatterns: list[URLPattern | URLResolver] = [
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    path('robots.txt', RobotsView.as_view(), name='robots'),
]

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('accounts/', include('custom_auth.urls')),
    path('profile/', include('user_profile.urls')),
    path('tools/', include('tools.urls')),
    prefix_default_language=False,
)

if settings.DEBUG:  # pragma: no cover
    from debug_toolbar.toolbar import debug_toolbar_urls

    urlpatterns += debug_toolbar_urls()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
