from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from posts.models import Group, Post


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = get_user_model().objects.create(username='TestUser')
        cls.user_two = get_user_model().objects.create(username='TestUserTwo')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовое описание',
            slug='test-slug',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_two = Client()
        self.authorized_client_two.force_login(self.user_two)
        self.template_url_names = {
            'posts/new.html': '/new/',
            'index.html': '/',
            'group.html': '/group/test-slug/',
            'posts/profile.html': '/TestUser/',
            'posts/post.html': '/TestUser/1/',
            'follow.html': '/follow/',
        }
        self.urls_availabel_guest = [
            '/',
            '/group/test-slug/',
            '/TestUser/',
            '/TestUser/1/',
        ]
        self.urls_available_authorized = [
            '/new/',
            '/TestUser/1/edit/',
            '/follow/',
        ]

    def test_urls_available_to_guest(self):
        """Страница доступна неавторизованному пользователю."""
        for url in self.urls_availabel_guest:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_urls_available_to_authorized(self):
        """Страница доступна авторизованному пользователю."""
        for url in [*self.urls_available_authorized,
                    *self.urls_availabel_guest]:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_url_redirect_annonymus_on_admin_login(self):
        """Страница доступная только авторизованному пользователю
        перенаправит анонимного пользователя на страницу логина.
        """
        for url in self.urls_available_authorized:
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(
                    response, ('/auth/login/?next='+url)
                )

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for template, url in self.template_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_edit_page_redirects_not_author(self):
        """Страница редактирование поста перенапраляет не автора."""
        response = self.authorized_client_two.get(
            '/TestUser/1/edit/',
            follow=True
        )
        self.assertRedirects(response, '/TestUser/1/')

    def test_404_page(self):
        """Несуществующая страница возвращает код 404"""
        response = self.guest_client.get('/abs/')
        self.assertEqual(response.status_code, 404)
