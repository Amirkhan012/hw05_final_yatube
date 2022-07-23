from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

User = get_user_model()


class AboutTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='Chelovek_Pavuk')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_url_about(self):
        """Проверка about URL-адресов."""
        templates_urls_names = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html',
        }
        for address, template in templates_urls_names.items():
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertTemplateUsed(response, template)
                self.assertEqual(response.status_code, HTTPStatus.OK)
        for address, template in templates_urls_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
                self.assertEqual(response.status_code, HTTPStatus.OK)
