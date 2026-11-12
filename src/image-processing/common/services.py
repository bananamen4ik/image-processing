"""Provides basic business logic."""

from django.conf import settings
from django.http import HttpRequest


def get_ip(request: HttpRequest) -> str:
    """Returns the current IP address.

    Return '0.0.0.0' if during testing using client.login or client.force_login.
    """
    x_real_ip = request.headers.get('x-real-ip')
    remote_addr = request.META.get('REMOTE_ADDR')

    if settings.TESTING and not x_real_ip and not remote_addr:
        return '0.0.0.0'

    return str(x_real_ip) if x_real_ip else str(remote_addr)
