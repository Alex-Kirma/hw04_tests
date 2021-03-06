from django.test import TestCase, Client
from django.contrib.auth import get_user_model

from http import HTTPStatus

from posts.models import Group, Post

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.post = Post.objects.create(
            text='Текст',
            author=cls.user,
        )
        cls.group = Group.objects.create(
            title='Тестовй заголовок',
            slug='test-slug',
            description='Описание группы',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_status_code_and_correct_template_guest_client(self):
        """Проверка доступа к странице и шаблону для
        неавторизированного пользователя."""
        templates_url_name = {
            'posts/index.html': '/',
            'posts/group_list.html': f'/group/{self.group.slug}/',
            'posts/profile.html': f'/profile/{self.user.username}/',
            'posts/post_detail.html': f'/posts/{self.post.pk}/',
        }
        for template, address in templates_url_name.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)

    def test_urls_status_code_and_correct_template_authorized_client(self):
        """Проверка доступа к странице и шаблону для авторизированного пользователя
        и редиректа неавторизированного пользователя."""
        templates_url_name = {
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.pk}/edit/': 'posts/create_post.html',
        }
        for address, template in templates_url_name.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, 302)

    def test_urls_status_code_guest_client_404(self):
        """Проверка доступа неавторизированного пользователя
        к несуществующей странице."""
        response = self.guest_client.get('posts/test/')
        self.assertEqual(response.status_code, 404)
