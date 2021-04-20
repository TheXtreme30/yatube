import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.test.utils import override_settings
from django.urls import reverse

from posts.models import Follow, Group, Post

USERNAME = 'TestUser'
SLUG = 'test-slug'
INDEX_URL = reverse('index')
FOLLOW_INDEX_URL = reverse('follow_index')
GROUP_URL = reverse('group', args=(SLUG,))
PROFILE_URL = reverse('profile', args=(USERNAME,))
NEW_POST_URL = reverse('new_post')
MEDIA_ROOT = tempfile.mkdtemp()
SMALL_GIF = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
             b'\x01\x00\x80\x00\x00\x00\x00\x00'
             b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
             b'\x00\x00\x00\x2C\x00\x00\x00\x00'
             b'\x02\x00\x01\x00\x00\x02\x02\x0C'
             b'\x0A\x00\x3B')


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.user = get_user_model().objects.create(username=USERNAME)
        cls.user_one = get_user_model().objects.create(username='TestUser1')
        cls.group_one = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовое описание',
            slug=SLUG,
        )
        cls.group_two = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовое описание',
            slug='test-slug-2',
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        Post.objects.bulk_create(Post(
            text=f'Тестовый текст {i}',
            author=cls.user,
            group=cls.group_one,
            image=uploaded,
            ) for i in range(1, 13)
        )
        cls.post = Post.objects.first()
        cls.post_url = reverse('post', args=(USERNAME, cls.post.id))
        cls.edit_url = reverse('post_edit', args=(USERNAME, cls.post.id))
        cls.comment_url = reverse('add_comment', args=(USERNAME, cls.post.id))
        cls.profile_follow = reverse('profile_follow', args=(cls.user,))
        cls.profile_unfollow = reverse('profile_unfollow', args=(cls.user,))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_one = Client()
        self.authorized_client_one.force_login(self.user_one)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            'posts/new.html': NEW_POST_URL,
            'index.html': INDEX_URL,
            'group.html': GROUP_URL,
            'posts/profile.html': PROFILE_URL,
            'posts/post.html': self.post_url,
            'follow.html': FOLLOW_INDEX_URL,
        }
        for template, reverse_name in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформированы с правильным контекстом."""
        response = self.authorized_client.get(INDEX_URL)
        context = response.context['page']
        self.assertEqual(list(context), list(Post.objects.all()[:10]))

    def test_group_page_show_correct_context(self):
        """Шаблон group сформированы с правильным контекстом."""
        response = self.authorized_client.get(GROUP_URL)
        context = response.context['page'].object_list
        self.assertEqual(context, list(self.group_one.posts.all()[:10]))

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформированы с правильным контекстом."""
        response = self.authorized_client.get(PROFILE_URL)
        context = response.context['page'].object_list
        self.assertEqual(context, list(self.user.posts.all()[:10]))

    def test_post_page_show_correct_context(self):
        """Шаблон post сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.post_url)
        context = response.context['post']
        self.assertEqual(context, self.post)

    def test_new_page_show_correct_context(self):
        """Шаблон new сформирован с правильным контекстом."""
        response = self.authorized_client.get(NEW_POST_URL)
        form_field = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_field.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_posts_not_in_another_group(self):
        """Пост не попадает в другую группу."""
        response = self.authorized_client.get(
            reverse('group', args=('test-slug-2',))
        )
        self.assertFalse(response.context.get('posts'))

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.edit_url)
        context = response.context['post']
        self.assertEqual(context, self.post)

    def test_cache(self):
        """Проверка кэширования главной страницы."""
        response = self.authorized_client.get(INDEX_URL)
        content_first = response.content
        Post.objects.create(text='Текст', author=self.user)
        response = self.authorized_client.get(INDEX_URL)
        content_second = response.content
        self.assertEqual(content_first, content_second)

    def test_follow(self):
        """Авторизованный пользователь может
        подписываться на других пользователей.
        """
        self.authorized_client_one.get(self.profile_follow)
        follow = Follow.objects.filter(
            user=self.user_one,
            author=self.user
        ).exists()
        self.assertTrue(follow)

    def test_unfollow(self):
        """Авторизованный пользователь может
        удалять других пользователей  из подписок.
        """
        self.authorized_client_one.get(self.profile_follow)
        self.authorized_client_one.get(self.profile_unfollow)
        follow = Follow.objects.filter(
            user=self.user_one,
            author=self.user
        ).exists()
        self.assertFalse(follow)

    def test_follow_index(self):
        """
        Новая запись пользователя появляется в ленте тех, кто на него подписан
        и не появляется в ленте тех, кто не подписан на него.
        """
        Follow.objects.create(user=self.user_one, author=self.user)
        response = self.authorized_client_one.get(FOLLOW_INDEX_URL)
        context = response.context['page'].object_list
        self.assertEqual(list(context), list(self.user.posts.all()[:10]))
        response = self.authorized_client.get(FOLLOW_INDEX_URL)
        context = response.context['page'].object_list
        self.assertNotEqual(list(context), list(self.user.posts.all()[:10]))
