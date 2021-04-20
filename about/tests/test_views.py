from django.test import Client, TestCase
from django.urls.base import reverse


class AboutViewsTests(TestCase):
    def setUp(self):
        super().setUp()
        self.guest_client = Client()

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_page_name = {
            'about/author.html': reverse('about:author'),
            'about/tech.html': reverse('about:tech'),
        }
        for template, revese_name in templates_page_name.items():
            with self.subTest(template=template):
                response = self.guest_client.get(revese_name)
                self.assertTemplateUsed(response, template)
