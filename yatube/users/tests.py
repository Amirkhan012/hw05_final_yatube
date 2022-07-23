from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

User = get_user_model()


class UsersTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='Chelovek_Pavuk')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.templates_urls_names_auth = {
            reverse('users:password_change'):
                'users/password_change_form.html',
            reverse('users:password_change_done'):
                'users/password_change_done.html',
            reverse('users:logout'):
                'users/logged_out.html',
            reverse('users:login'):
                'users/login.html',
            reverse('users:password_reset_form'):
                'users/password_reset_form.html',
            reverse('users:password_reset_done'):
                'users/password_reset_done.html',
            reverse('users:password_reset_confirm',
                    kwargs={'uidb64': 'MTA', 'token':
                            'a88hdr-5fb0f72acbe1e9d2b81b7810dee31037'}):
                'users/password_reset_confirm.html',
            reverse('users:password_reset_complete'):
                'users/password_reset_complete.html',
        }
        self.templates_urls_names_guest = {
            reverse('users:logout'):
                'users/logged_out.html',
            reverse('users:login'):
                'users/login.html',
            reverse('users:password_reset_form'):
                'users/password_reset_form.html',
            reverse('users:password_reset_done'):
                'users/password_reset_done.html',
            reverse('users:password_reset_confirm',
                    kwargs={'uidb64': 'MTA', 'token':
                            'a88hdr-5fb0f72acbe1e9d2b81b7810dee31037'}):
                'users/password_reset_confirm.html',
            reverse('users:password_reset_complete'):
                'users/password_reset_complete.html',
        }

    def test_url_users_guest(self):
        """Проверка users URL-адресов на
        запросы неавторизированного пользователя."""
        for address, template in self.templates_urls_names_guest.items():
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertTemplateUsed(response, template)
                self.assertEqual(response.status_code, HTTPStatus.OK)
        response = self.client.get(reverse('users:password_change'))
        self.assertEqual(response.status_code, HTTPStatus.FOUND.value,
                         'Users: password_change code-302 failed')
        response = self.client.get(reverse('users:password_change_done'))
        self.assertEqual(response.status_code, HTTPStatus.FOUND.value,
                         'Users: password_change/done/ code-302 failed')

    def test_url_users_auth(self):
        """Проверка users URL-адресов на
        запросы авторизированного пользователя."""
        for address, template in self.templates_urls_names_auth.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
                self.assertEqual(response.status_code, HTTPStatus.OK)
