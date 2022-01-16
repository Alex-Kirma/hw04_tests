from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from posts.models import Post, Group


User = get_user_model()


class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.group_1 = Group.objects.create(
            title='Тестовй заголовок_1',
            slug='test-slug_1',
            description='Описание группы_1'
        )
        cls.group_2 = Group.objects.create(
            title='Тестовй заголовок_2',
            slug='test-slug_2',
            description='Описание группы_2'
        )
        cls.group_3 = Group.objects.create(
            title='Тестовй заголовок_3',
            slug='test-slug_3',
            description='Описание группы_3'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст поста',
            author=cls.user,
            group=cls.group_1,
            pk=1,
        )
        cls.post_test = Post.objects.create(
            text='Тестовый текст test',
            author=cls.user,
            group=cls.group_2,
            pk=2,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_page_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:posts_list', kwargs={
                'slug': 'test-slug_1'}): 'posts/group_list.html',
            reverse('posts:profile', kwargs={
                'username': 'test_user'}): 'posts/profile.html',
            reverse('posts:post_detail', kwargs={
                'post_id': '1'}): 'posts/post_detail.html',
            reverse('posts:create_post'): 'posts/create_post.html',
            reverse('posts:edit', kwargs={
                'post_id': '1'}): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        posts_text_0 = first_object.text
        posts_author_0 = first_object.author
        self.assertEqual(posts_text_0, 'Тестовый текст поста')
        self.assertEqual(posts_author_0, self.user)

    def test_group_post_page_show_correct_context(self):
        response = self.authorized_client.get(

            reverse('posts:posts_list', kwargs={'slug': 'test-slug_1'}))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        self.assertEqual(post_text_0, 'Тестовый текст поста')
        self.assertEqual(
            response.context['group'].title, 'Тестовй заголовок_1')
        self.assertEqual(
            response.context['group'].description, 'Описание группы_1')

    def test_profile_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'test_user'}))
        number_of_posts_test = Post.objects.count()
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        self.assertEqual(post_text_0, 'Тестовый текст поста')
        self.assertEqual(response.context['author'], self.user)
        self.assertEqual(
            response.context['number_of_posts'], number_of_posts_test)

    def test_post_detail_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': '1'}))
        self.assertEqual(response.context.get(
            'post').text, 'Тестовый текст поста')

    def test_page_create_post_form_correct_context_(self):
        """Провертка формы create_post """
        response = self.authorized_client.get(reverse('posts:create_post'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_page_edit_post_form_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:edit', kwargs={'post_id': '1'}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

        self.assertEqual(response.context.get('is_edit'), True)

    def test_post_group(self):
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][1]
        post_text_1 = first_object.text
        self.assertEqual(post_text_1, 'Тестовый текст test')

        response = self.authorized_client.get(
            reverse('posts:posts_list', kwargs={'slug': 'test-slug_2'}))
        first_object = response.context['page_obj'][0]
        post_text_1 = first_object.text
        self.assertEqual(post_text_1, 'Тестовый текст test')
        response = self.authorized_client.get(
            reverse('posts:posts_list', kwargs={'slug': 'test-slug_3'}))
        self.assertEqual(len(response.context['page_obj']), 0)

        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'test_user'}))
        first_object = response.context['page_obj'][1]
        post_text_1 = first_object.text
        self.assertEqual(post_text_1, 'Тестовый текст test')


class PaginatorPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='Тестовй заголовок',
            slug='test-slug',
            description='Описание группы'
        )
        for i in range(0, 15):
            Post.objects.create(
                author=cls.user,
                text=f'Тестовый текст поста {i}',
                group=cls.group)

    def setUp(self):
        self.guest_client = Client()

    def test_index_page_paginator(self):
        """Тестрование пагинатора index, всего постов 15."""
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 5)

    def test_group_list_page_paginator(self):
        """Тестрование пагинатора group_list, всего постов 15.."""
        response = self.client.get(
            reverse('posts:posts_list', kwargs={'slug': 'test-slug'}))
        self.assertEqual(len(response.context['page_obj']), 10)
        response = self.client.get(reverse('posts:posts_list', kwargs={
                                   'slug': 'test-slug'}) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 5)

    def test_profile_page_paginator(self):
        """Тестрование пагинатора profile, всего постов 15 автора test_user"""
        response = self.client.get(
            reverse('posts:profile', kwargs={'username': 'test_user'}))
        self.assertEqual(len(response.context['page_obj']), 10)
        response = self.client.get(reverse('posts:profile', kwargs={
                                   'username': 'test_user'}) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 5)
