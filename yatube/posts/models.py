from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        verbose_name='Заголовок',
        max_length=200,
        help_text='Описание заголовка группы'
    )
    slug = models.SlugField(
        verbose_name='Адрес',
        unique=True,
        help_text='Адрес страницы группы'
    )
    description = models.TextField(
        verbose_name='Описание',
        help_text='Описание группы'
    )

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        'Текст поста',
        help_text='Введите текст поста'
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        help_text='Дата публикации поста',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        help_text='Автор поста',
        related_name='posts',
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        related_name='posts',
        blank=True,
        null=True,
        verbose_name='Группа',
        help_text='Выберите группу',
    )

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.text
