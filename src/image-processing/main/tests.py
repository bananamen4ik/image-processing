"""Provides tests for the application."""

from django.test import SimpleTestCase
from django.urls import reverse


class IndexPageTest(SimpleTestCase):
    """Tests for the main page."""

    def test_index(self) -> None:
        """Checking that the page is accessible."""
        response = self.client.get(reverse('main:index'))
        self.assertEqual(response.status_code, 200)


class PlansPageTest(SimpleTestCase):
    """Tests for the plans page."""

    def test_plans(self) -> None:
        """Checking that the page is accessible."""
        response = self.client.get(reverse('main:plans'))
        self.assertEqual(response.status_code, 200)


class AboutPageTest(SimpleTestCase):
    """Tests for the about page."""

    def test_about(self) -> None:
        """Checking that the page is accessible."""
        response = self.client.get(reverse('main:about'))
        self.assertEqual(response.status_code, 200)
