import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.test.utils import override_settings
from django.urls import reverse

from posts.models import Group, Post

MEDIA_ROOT = tempfile.mkdtemp()
SMALL_GIF = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
             b'\x01\x00\x80\x00\x00\x00\x00\x00'
             b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
             b'\x00\x00\x00\x2C\x00\x00\x00\x00'
             b'\x02\x00\x01\x00\x00\x02\x02\x0C'
             b'\x0A\x00\x3B')


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.user = get_user_model().objects.create(username='TestUser')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовое описание',
            slug='test-slug',
        )
        cls.group_two = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовое описание',
            slug='test-slug-2',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Форма создает запись."""
        posts_count = Post.objects.count()
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        post = response.context['page'][0]
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.id, form_data['group'])
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.image.file.read(),
                         form_data['image'].file.getvalue())
        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_edit_post(self):
        """Форма редактирует запись"""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Редактированный текст',
            'group': self.group_two.id
        }
        response = self.authorized_client.post(
            reverse(
                'post_edit',
                kwargs={'username': self.user, 'post_id': self.post.id}
            ),
            data=form_data,
            follow=True
        )
        self.post.refresh_from_db()
        self.assertRedirects(response, reverse(
            'post',
            kwargs={'username': self.user, 'post_id': self.post.id}
        ))
        self.assertEqual(self.post.text, form_data['text'])
        self.assertEqual(self.post.group.id, form_data['group'])
        self.assertEqual(Post.objects.count(), posts_count)
