from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post


class ModelsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = get_user_model().objects.create(username='testuser')
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

    def test_post_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post = ModelsTests.post
        field_verboses = {
            'text': 'Текст',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
            'image': 'Изображение',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected
                )

    def test_post_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        post = ModelsTests.post
        field_help_texts = {
            'text': 'Введите текст',
            'group': 'Укажите группу',
            'image': 'Загрузите изображение',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected
                )

    def test_post_object_name_is_text_field(self):
        """__str__  post - это строчка с содержимым post.text[:15]."""
        post = ModelsTests.post
        expected_object_name = post.text[:15]
        self.assertEquals(expected_object_name, str(post))

    def test_group_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        group = ModelsTests.group
        field_verboses = {
            'title': 'Заголовок',
            'description': 'Описание',
            'slug': 'Адрес для страницы',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).verbose_name, expected
                )

    def test_group_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        group = ModelsTests.group
        field_help_texts = {
            'description': 'Опишите группу',
            'slug': 'Укажите адрес для страницы задачи. Используйте '
                    'только латиницу, цифры, дефисы и знаки '
                    'подчёркивания'
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).help_text, expected
                )

    def test_group_object_name_is_title_fild(self):
        """__str__  group - это строчка с содержимым group.text[:15]."""
        group = ModelsTests.group
        expected_object_name = group.title
        self.assertEquals(expected_object_name, str(group))
