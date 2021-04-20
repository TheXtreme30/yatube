from django.test import Client, TestCase


class AboutURLTests(TestCase):
    def setUp(self):
        super().setUp()
        self.guest_client = Client()

    def test_urls_exists_at_desired_location(self):
        """Страница доступна любому пользователю."""
        urls_name = [
            '/about/author/',
            '/about/tech/',
        ]
        for url in urls_name:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200)
