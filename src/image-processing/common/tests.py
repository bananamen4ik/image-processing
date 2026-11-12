"""Provides tests for the common application."""

from typing import cast

from django.test import (
    RequestFactory,
    TestCase,
)
from django.utils.translation.trans_real import get_languages

from common.services import get_ip
from common.templatetags.common_basic import (
    get_uris_languages,
    uri_to_language,
)


class TagUriToLanguageTests(TestCase):
    """Tests tag."""

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


class TagGetUrisLanguagesTests(TestCase):
    """Tests tag."""

    def test_get_uris_languages(self) -> None:
        """Tests the retrieval of all language variants of a URI."""
        uris = get_uris_languages('/some/uri')
        self.assertEqual(len(uris), len(get_languages()))


class GetIpTests(TestCase):
    """Tests get_ip function."""

    def setUp(self) -> None:
        """Sets up the request factory."""
        self.rf = RequestFactory()

    def test_remote_addr(self) -> None:
        """Tests getting the remote address."""
        ip = '127.0.0.1'
        get_request = self.rf.get('/some/uri')
        current_ip = get_ip(get_request)
        self.assertEqual(current_ip, ip)

    def test_x_real_ip(self) -> None:
        """Tests getting the x real ip header."""
        ip = '1.1.1.1'
        get_request = self.rf.get(
            '/some/uri',
            headers={
                'X-Real-Ip': ip,
            },
        )
        current_ip = get_ip(get_request)
        self.assertEqual(current_ip, ip)
