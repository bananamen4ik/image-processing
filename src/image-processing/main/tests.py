from django.test import SimpleTestCase
from django.urls import reverse


class IndexPageTest(SimpleTestCase):
    def test_index(self) -> None:
        response = self.client.get(reverse('main:index'))
        self.assertEqual(response.status_code, 200)
