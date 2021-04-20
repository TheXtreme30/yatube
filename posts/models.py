from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.deletion import CASCADE
from django.db.models.fields.related import ForeignKey

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        verbose_name='Заголовок',
        max_length=200
    )
    description = models.TextField(
        verbose_name='Описание',
        help_text='Опишите группу'
    )
    slug = models.SlugField(
        verbose_name='Адрес для страницы',
        unique=True,
        help_text=('Укажите адрес для страницы задачи. Используйте '
                   'только латиницу, цифры, дефисы и знаки '
                   'подчёркивания')
    )

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст',
        help_text='Введите текст'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='posts'
    )
    group = models.ForeignKey(
        Group,
        verbose_name='Группа',
        on_delete=models.SET_NULL,
        blank=True, null=True,
        related_name='posts',
        help_text='Укажите группу'
    )
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='posts/',
        blank=True,
        null=True,
        help_text='Загрузите изображение'
    )

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField(
        verbose_name='текст'
    )
    created = models.DateTimeField(
        auto_now_add=True
    )


class Follow(models.Model):
    user = ForeignKey(
        User,
        on_delete=CASCADE,
        related_name='follower',
    )
    author = ForeignKey(
        User,
        on_delete=CASCADE,
        related_name='following',
    )

    class Meta:
        constraints = models.UniqueConstraint(
            fields=['user', 'author'],
            name='ua'
        )
