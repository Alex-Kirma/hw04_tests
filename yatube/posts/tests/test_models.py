from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post

User = get_user_model()


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Заголовок теста группы',
            slug='Адрес тестовой страницы',
            description='Описание теста группы',
        )

    def test_verbose_name_group(self):
        """проверка verbose_name поля с ожидаемым."""
        group = GroupModelTest.group
        field_verboses = {
            'title': 'Заголовок',
            'slug': 'Адрес',
            'description': 'Описание',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).verbose_name, expected_value)

    def test_help_text(self):
        """Проверка help_text поля с ожидаемым."""
        group = GroupModelTest.group
        field_help_text = {
            'title': 'Описание заголовка группы',
            'slug': 'Адрес страницы группы',
            'description': 'Описание группы',
        }
        for field, expected_value in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).help_text, expected_value)

    def test_object_name_is_title_field_group(self):
        """__str__ group - проверка содержимого поля group."""
        group = GroupModelTest.group
        group_object_name_title = group.title
        self.assertEqual(group_object_name_title, str(group.title))


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            pub_date='Тестовая дата публикации',
        )

    def test_verbose_name_post(self):
        """проверка verbose_name поля с ожидаемым."""
        post = PostModelTest.post
        field_verbose_name = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        for field, expected_value in field_verbose_name.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value)

    def test_help_text_post(self):
        """проверка help_text поля с ожидаемым."""
        post = PostModelTest.post
        field_help_text = {
            'text': 'Введите текст поста',
            'pub_date': 'Дата публикации поста',
            'author': 'Автор поста',
            'group': 'Выберите группу',
        }
        for field, expected_value in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value)

    def test_object_name_is_text_field_post(self):
        """__str__ post - проверка содержимого поля post."""
        post = PostModelTest.post
        post_object_name_text = post.text
        self.assertEqual(post_object_name_text, str(post.text[:15]))
