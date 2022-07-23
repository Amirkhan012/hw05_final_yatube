from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from posts.models import Post, Group
from posts.views import PAGINATE_BY


User = get_user_model()

COUNT_POSTS = 25
LAST_PAGE = 5


class ViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.user_2 = User.objects.create_user(username='User-2')
        cls.user_3 = User.objects.create_user(username='User-3')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=ViewTests.user,
            text='Тестовый пост для проверки',
            group=cls.group
        )
        for i in range(24):
            Post.objects.create(
                author=ViewTests.user,
                text='Тестовый пост для проверки' + str(i),
                group=ViewTests.group,
            )

    def setUp(self):
        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(ViewTests.user_2)
        self.authorized_client_3 = Client()
        self.authorized_client_3.force_login(ViewTests.user_3)
        self.authorized_client = Client()
        self.authorized_client.force_login(ViewTests.user)
        self.form_fields = {
            'group': forms.ModelChoiceField,
            'text': forms.CharField,
            'image': forms.ImageField,
        }
        self.templates_pages_names = {
            reverse('posts:index'):
                'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': ViewTests.group.slug}):
                'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': ViewTests.user}):
                'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': ViewTests.post.pk}):
                'posts/post_detail.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': ViewTests.post.pk}):
                'posts/create_post.html',
            reverse('posts:post_create'):
                'posts/create_post.html',
        }
        cache.clear()

    def test_views_correct_namespace(self):
        """Проверка namespace во view-функциях."""
        for reverse_name, template in self.templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_views_index_paginator(self):
        """Проверка paginator в index view."""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), PAGINATE_BY)
        self.assertEqual(response.context['page_obj'].paginator.count,
                         COUNT_POSTS)
        response = self.client.get(reverse('posts:index') + '?page=3')
        self.assertEqual(len(response.context['page_obj']), LAST_PAGE)

    def test_views_index_context(self):
        """Проверка context в index view."""
        response = self.authorized_client.get(reverse('posts:index'))
        page = response.context['page_obj']
        first_object = page.paginator.object_list.order_by('id')[0]
        self.assertEqual(first_object.text, ViewTests.post.text)
        self.assertEqual(first_object.pk, ViewTests.post.pk)

    def test_views_post_delete(self):
        """Проверка post_delete."""
        user2 = User.objects.create_user(username='PAVUK')
        authorized_client2 = Client()
        authorized_client2.force_login(user2)
        post_count = Post.objects.all().count()
        self.client.get(reverse(
            'posts:post_delete',
            kwargs={'post_id': ViewTests.post.pk}))
        self.assertEqual(Post.objects.all().count(), post_count)
        authorized_client2.get(reverse(
            'posts:post_delete',
            kwargs={'post_id': ViewTests.post.pk}))
        self.assertEqual(Post.objects.all().count(), post_count)
        self.authorized_client.get(reverse(
            'posts:post_delete',
            kwargs={'post_id': ViewTests.post.pk}))
        self.assertEqual(Post.objects.all().count(), post_count - 1)

    def test_views_group_list_paginator(self):
        """Проверка paginator в group_list view."""
        response = self.authorized_client.get(reverse(
            'posts:group_list',
            kwargs={'slug': ViewTests.group.slug}))
        self.assertEqual(len(response.context['page_obj']), PAGINATE_BY)
        self.assertEqual(response.context['page_obj'].paginator.count,
                         COUNT_POSTS)
        response = self.authorized_client.get(reverse(
            'posts:group_list',
            kwargs={'slug': ViewTests.group.slug}) + '?page=3')
        self.assertEqual(len(response.context['page_obj']), LAST_PAGE)

    def test_views_group_list_context(self):
        """Проверка context в group_list view."""
        response = self.authorized_client.get(reverse(
            'posts:group_list',
            kwargs={'slug': ViewTests.group.slug}))
        self.assertEqual(response.context.get('group').title,
                         ViewTests.group.title)
        self.assertEqual(response.context.get('group').description,
                         ViewTests.group.description)
        self.assertEqual(response.context.get('group').slug,
                         ViewTests.group.slug)
        page = response.context['page_obj']
        first_object = page.paginator.object_list.order_by('id')[0]
        self.assertEqual(first_object.text, ViewTests.post.text)
        self.assertEqual(first_object.pk, ViewTests.post.pk)

    def test_views_profile_paginator(self):
        """Проверка paginator в profile view."""
        response = self.authorized_client.get(reverse(
            'posts:profile',
            kwargs={'username': ViewTests.user}))
        self.assertEqual(len(response.context['page_obj']), PAGINATE_BY)
        self.assertEqual(response.context['count'],
                         COUNT_POSTS)
        response = self.authorized_client.get(reverse(
            'posts:profile',
            kwargs={'username': ViewTests.user}) + '?page=3')
        self.assertEqual(len(response.context['page_obj']), LAST_PAGE)

    def test_views_profile_context(self):
        """Проверка context в profile view."""
        response = self.authorized_client.get(reverse(
            'posts:profile',
            kwargs={'username': ViewTests.user}))
        page = response.context['page_obj']
        first_object = page.paginator.object_list.order_by('id')[0]
        first_object = page.paginator.object_list.order_by('id')[0]
        self.assertEqual(first_object.text, ViewTests.post.text)
        self.assertEqual(first_object.pk, ViewTests.post.pk)

    def test_views_post_detail_context(self):
        """Проверка context в post_detail view."""
        response = self.authorized_client.get(reverse(
            'posts:post_detail',
            kwargs={'post_id': ViewTests.post.pk}))
        post = response.context['post']
        self.assertEqual(post.author, ViewTests.user)
        self.assertEqual(post.text, ViewTests.post.text)
        self.assertEqual(post.pk, ViewTests.post.pk)

    def test_views_post_edit_context(self):
        """Проверка context в post_edit view."""
        response = self.authorized_client.get(reverse(
            'posts:post_edit',
            kwargs={'post_id': ViewTests.post.pk}))
        for value, expected in self.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        self.assertEqual(response.context['is_edit'], True)

    def test_views_post_create_context(self):
        """Проверка context в post_create view."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        for value, expected in self.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_views_post_with_group(self):
        """Проверка появления поста с группой в предназначенных местах."""
        group2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test_slug2',
            description='Тестовое описание2',
        )
        Post.objects.create(
            author=ViewTests.user,
            text='Тестовый пост для проверки group2',
            group=group2
        )
        group_in_pages = {
            reverse('posts:index'): ViewTests.group,
            reverse('posts:group_list',
                    kwargs={'slug': ViewTests.group.slug}): ViewTests.group,
            reverse('posts:group_list',
                    kwargs={'slug': group2.slug}): ViewTests.group,
            reverse('posts:profile',
                    kwargs={'username': ViewTests.user}): ViewTests.group,
        }
        for reverse_name, group in group_in_pages.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                post_group = response.context['page_obj'][0].group
                if post_group == group2:
                    self.assertNotEqual(post_group, group)
                else:
                    self.assertEqual(post_group, group)

    def test_cache_index(self):
        """Проверка кеша в index."""
        response = self.client.get(reverse(
            'posts:index'
        ))
        Post.objects.create(
            author=ViewTests.user,
            text='Пост для проверки кеша',
            group=ViewTests.group
        )
        self.assertEqual(
            response.content,
            self.client.get(reverse(
                'posts:index'
            )).content
        )
        cache.clear()
        self.assertNotEqual(
            response.content,
            self.client.get(reverse(
                'posts:index'
            )).content
        )

    def test_user_follow(self):
        """Проверка авторизованного пользователя
        на возможность подписаться и удаление подписки."""
        follower_count = ViewTests.user_2.follower.count()
        following_count = ViewTests.user.follower.count()
        self.authorized_client_2.get(reverse(
            'posts:profile_follow',
            kwargs={'username': ViewTests.user})
        )
        self.assertEqual(ViewTests.user_2.follower.count(), follower_count + 1)
        self.assertEqual(ViewTests.user.following.count(), following_count + 1)
        self.authorized_client_2.get(reverse(
            'posts:profile_unfollow',
            kwargs={'username': ViewTests.user})
        )
        self.assertEqual(ViewTests.user_2.follower.count(), follower_count)
        self.assertEqual(ViewTests.user.following.count(), following_count)

    def test_guest_follow(self):
        """Проверка неавторизованного пользователя
        на возможность подписаться и удаление подписки."""
        following_count = ViewTests.user.follower.count()
        self.client.get(reverse(
            'posts:profile_follow',
            kwargs={'username': ViewTests.user})
        )
        self.assertEqual(ViewTests.user.following.count(), following_count)

    def test_posts_following(self):
        """Проверка на появление записи пользователя в
        ленте тех, кто на него подписан и тех, кто не подписан."""
        Post.objects.create(
            author=ViewTests.user_2,
            text='Жду подписку от User-3',
            group=ViewTests.group
        )
        self.authorized_client_2.get(reverse(
            'posts:profile_follow',
            kwargs={'username': ViewTests.user})
        )
        self.authorized_client_3.get(reverse(
            'posts:profile_follow',
            kwargs={'username': ViewTests.user_2})
        )
        following_posts_user_2 = Post.objects.filter(
            author__following__user=ViewTests.user_2
        )
        following_posts_user_3 = Post.objects.filter(
            author__following__user=ViewTests.user_3
        )
        last_post_following_user_2 = following_posts_user_2.order_by('-id')[0]
        last_post_following_user_3 = following_posts_user_3.order_by('-id')[0]
        self.assertNotEqual(
            last_post_following_user_2,
            last_post_following_user_3
        )
        Post.objects.create(
            author=ViewTests.user,
            text='Конечная проверка',
            group=ViewTests.group
        )
        last_post_following_user_2 = following_posts_user_2.order_by('-id')[0]
        last_post_following_user_3 = following_posts_user_3.order_by('-id')[0]
        self.assertNotEqual(
            last_post_following_user_2,
            last_post_following_user_3
        )
