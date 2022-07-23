from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase, Client

from posts.models import Group, Post

User = get_user_model()


class URLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user1 = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=URLTests.user1,
            text='Тестовый пост для проверки',
        )

    def setUp(self):
        self.user2 = User.objects.create_user(username='Chelovek_Pavuk')
        self.authorized_client_1 = Client()
        self.authorized_client_1.force_login(self.user1)
        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(self.user2)
        self.templates_urls_auth = {
            '': 'posts/index.html',
            f'/group/{URLTests.group.slug}/': 'posts/group_list.html',
            f'/profile/{URLTests.user1}/': 'posts/profile.html',
            f'/posts/{URLTests.post.pk}/': 'posts/post_detail.html',
            f'/posts/{URLTests.post.pk}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }
        self.templates_urls_guest = {
            '': 'posts/index.html',
            f'/group/{URLTests.group.slug}/': 'posts/group_list.html',
            f'/profile/{URLTests.user1}/': 'posts/profile.html',
            f'/posts/{URLTests.post.pk}/': 'posts/post_detail.html',
        }
        cache.clear()

    def test_urls_guest(self):
        """Проверка URL-адресов на запросы неавторизированного пользователя."""
        for address, template in self.templates_urls_guest.items():
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertTemplateUsed(response, template)
                self.assertEqual(response.status_code, HTTPStatus.OK)
        response = self.client.get("/create/")
        self.assertEqual(response.status_code, HTTPStatus.FOUND.value,
                         'URLs: guest code-302 failed')

    def test_urls_auth(self):
        """Проверка URL-адресов на запросы авторизированного пользователя."""
        for address, template in self.templates_urls_auth.items():
            with self.subTest(address=address):
                response = self.authorized_client_1.get(address)
                self.assertTemplateUsed(response, template)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_edit_302(self):
        response = self.authorized_client_2.get(
            f'/posts/{URLTests.post.pk}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND.value)
        response = self.client.get(
            f'/posts/{URLTests.post.pk}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND.value)

    def test_urls_404(self):
        response = self.client.get('/not_found_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND.value)
        self.assertTemplateUsed(response, 'core/404.html')
