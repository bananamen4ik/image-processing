"""Provides tests for the common application."""

from typing import cast

from django.test import TestCase

from common.templatetags.common_basic import uri_to_language


class TagUriToLanguageTests(TestCase):
    """Tests for the simple tag."""

    def test_uris(self) -> None:
        """Tests a set of URIs."""
        uris = (
            {
                'uri': '/some/uri',
                'expected_results': {
                    'en': '/some/uri',
                    'ru': '/ru/some/uri',
                },
            },
            {
                'uri': '/ru/some/uri',
                'expected_results': {
                    'en': '/some/uri',
                    'ru': '/ru/some/uri',
                },
            },
        )

        for uri_data in uris:
            uri = cast(str, uri_data['uri'])
            expected_results = cast(dict[str, str], uri_data['expected_results'])

            for language_code, expected_result in expected_results.items():
                result_uri = uri_to_language(uri, language_code)
                self.assertEqual(result_uri, expected_result)
