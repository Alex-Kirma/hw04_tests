from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from http import HTTPStatus

from posts.models import Post, Group


User = get_user_model()


class FormsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='Тестовый заголовок группы',
            slug='test-slug',
            description='Описание группы',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст поста',
            author=cls.user,
            group=cls.group,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.guest_client = Client()

    def test_form_post_create(self):
        """Проверка создания поста."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст поста',
            'group': 1,
        }
        self.authorized_client.post(
            reverse('posts:create_post'),
            data=form_data,
            follow=True
        )
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        last_post = Post.objects.first()
        self.assertEqual(last_post.text, self.post.text)
        self.assertEqual(last_post.author, self.post.author)
        self.assertEqual(last_post.group, self.post.group)

    def test_form_post_edit(self):
        """Проверка редактирования поста."""
        form_data = {
            'text': 'Редактированный текст поста',
            'group': 1,
        }

        self.authorized_client.post(
            reverse('posts:edit', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)
        post = Post.objects.get(pk=self.post.pk)
        self.assertEqual(post.text, form_data['text'])
        last_post = Post.objects.first()
        self.assertEqual(last_post.text, 'Редактированный текст поста')
        self.assertEqual(last_post.author, self.post.author)
        self.assertEqual(last_post.group, self.post.group)

    def test_guest_client_create_post(self):
        """Проверка что неавторизованный пользователь не может создать
         пост и редирект его на страницу авторизации."""
        posts_count = Post.objects.count()
        response = self.guest_client.post(reverse('posts:create_post'))
        self.assertRedirects(response, reverse('users:login') + '?next='
                             + reverse('posts:create_post'),
                             status_code=302, target_status_code=200)
        form_data = {
            'text': 'Тестовый текст поста',
            'group': 1,
        }
        self.guest_client.post(
            reverse('posts:create_post'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count)
