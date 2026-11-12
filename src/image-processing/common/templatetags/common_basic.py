"""Registering basic django tags and templates."""

from django import template
from django.conf import settings
from django.utils.translation.trans_real import (
    get_language_from_path,
    get_languages,
)

register = template.Library()


@register.simple_tag
def uri_to_language(full_path: str, to_language: str) -> str:
    """Converts a URI to the specified language."""
    clean_path = full_path
    path_language = get_language_from_path(full_path)

    if path_language is not None:
        clean_path = full_path.replace(f'/{path_language}', '')

    if to_language != settings.LANGUAGE_CODE:
        clean_path = f'/{to_language}{clean_path}'

    return clean_path


@register.simple_tag
def get_uris_languages(full_path: str) -> list[str]:
    """Returns URI variants for all languages."""
    uris = []

    for language_code in get_languages():
        uris.append(uri_to_language(full_path, language_code))

    return uris
