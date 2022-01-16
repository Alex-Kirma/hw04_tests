from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post


User = get_user_model()


class FormsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.post = Post.objects.create(
            text='Тестовый текст поста',
            author=cls.user,
            pk=1
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_form_post_create(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст поста'
        }

        self.authorized_client.post(
            reverse('posts:create_post'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_form_post_edit(self):
        form_data = {
            'text': 'Редактированный текст поста'
        }

        self.authorized_client.post(
            reverse('posts:edit', kwargs={'post_id': '1'}),
            data=form_data,
            follow=True
        )
        post = Post.objects.get(pk=1)
        self.assertEqual(post.text, form_data['text'])
