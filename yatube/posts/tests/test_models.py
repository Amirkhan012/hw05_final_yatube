from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post

User = get_user_model()


class ModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост для проверки',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = ModelTest.post
        group = ModelTest.group
        expecteded_text = post.text
        expecteded_title = group.title
        self.assertEqual(expecteded_text, str(post),
                         'Ошибка: Post __str__ работает некорректно')
        self.assertEqual(expecteded_title, str(group),
                         'Ошибка: Group __str__ работает некорректно')

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post = ModelTest.post
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата создания',
            'author': 'Автор',
            'group': 'Группа',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value)

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        post = ModelTest.post
        help_texts = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост',
        }
        for field, expected_value in help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value)
