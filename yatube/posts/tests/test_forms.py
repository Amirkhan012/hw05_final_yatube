import shutil
import tempfile

from django.core.cache import cache
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Post, Group

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostCreateFormTests.user)
        self.small_gif = (
             b'\x47\x49\x46\x38\x39\x61\x02\x00'
             b'\x01\x00\x80\x00\x00\x00\x00\x00'
             b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
             b'\x00\x00\x00\x2C\x00\x00\x00\x00'
             b'\x02\x00\x01\x00\x00\x02\x02\x0C'
             b'\x0A\x00\x3B'
        )
        self.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=self.small_gif,
            content_type='image/gif'
        )
        self.big_gif = (
             b'\x47\x49\x46\x38\x39\x61\x02\x00'
             b'\x01\x00\x80\x00\x00\x00\x00\x00'
             b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
             b'\x00\x00\x00\x2C\x00\x00\x00\x00'
             b'\x02\x00\x01\x00\x00\x02\x02\x0C'
             b'\x0A\x00\x3B'
        )
        self.uploaded_2 = SimpleUploadedFile(
            name='big.gif',
            content=self.big_gif,
            content_type='image/gif'
        )
        self.another_gif = (
             b'\x47\x49\x46\x38\x39\x61\x02\x00'
             b'\x01\x00\x80\x00\x00\x00\x00\x00'
             b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
             b'\x00\x00\x00\x2C\x00\x00\x00\x00'
             b'\x02\x00\x01\x00\x00\x02\x02\x0C'
             b'\x0A\x00\x3B'
        )
        self.uploaded_3 = SimpleUploadedFile(
            name='another.gif',
            content=self.another_gif,
            content_type='image/gif'
        )
        self.post = Post.objects.create(
            author=PostCreateFormTests.user,
            text='Тестовый пост для проверки',
            group=PostCreateFormTests.group,
            image=self.uploaded_2
        )
        self.templates_pages_names = {
            reverse('posts:index'):
                self.post.image,
            reverse('posts:group_list',
                    kwargs={'slug': PostCreateFormTests.group.slug}):
                self.post.image,
            reverse('posts:profile',
                    kwargs={'username': PostCreateFormTests.user}):
                self.post.image,
        }
        cache.clear()

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        form_data = {
            'text': 'Тестовый текст 2',
            'group': PostCreateFormTests.group.pk,
            'image': self.uploaded,
        }
        posts_count = Post.objects.count()
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse(
            'posts:profile',
            args=(PostCreateFormTests.user.username,)))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        post = Post.objects.all().order_by('-id')[0]
        self.assertEqual(form_data['text'], post.text)
        self.assertEqual(form_data['group'], post.group.pk)
        self.assertIn(form_data['image'].name, post.image.name)

    def test_create_post_garbage_image(self):
        """Создание записи в Post с мусорной картинкой."""
        garbage_gif = (
            b'\xd0\x91\xd0\xb0\xd0\xb9\xd1\x82\xd1\x8b'
        )
        garbage_uploaded = SimpleUploadedFile(
            name='garbage_gif.gif',
            content=garbage_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый текст 2',
            'group': PostCreateFormTests.group.pk,
            'image': garbage_uploaded,
        }
        posts_count = Post.objects.count()
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertEqual(Post.objects.count(), posts_count)

    def test_edit_post(self):
        """Валидная форма редактирования записи в Post."""
        group2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test_slug2',
            description='Тестовое описание2',
        )
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Измененный текст',
            'group': group2.pk,
        }
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            args=(self.post.pk,)))
        edit_post = Post.objects.get(id=self.post.pk)
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(form_data['text'], edit_post.text)
        self.assertEqual(form_data['group'], edit_post.group.pk)
        self.assertEqual(self.post.image, edit_post.image)

    def test_edit_post_with_image(self):
        """Редактирования записи в Post с изменением картинки на другую."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Измененный текст',
            'image': self.uploaded_3,
        }
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            args=(self.post.pk,)))
        edit_post = Post.objects.get(id=self.post.pk)
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(form_data['text'], edit_post.text)
        self.assertNotEqual(self.post.group, edit_post.group)
        self.assertIn(form_data['image'].name, edit_post.image.name)

    def test_images_in_context_views(self):
        """Проверка при выводе поста с картинкой изображение передаётся в словаре
        context в views функциях."""
        for reverse_name, image in self.templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                page = response.context['page_obj']
                first_object = page.paginator.object_list.order_by('id')[0]
                self.assertEqual(first_object.image, image)
        response = self.authorized_client.get(reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.pk}))
        first_object = response.context['post']
        self.assertEqual(first_object.image, self.post.image)

    def test_comment_guest(self):
        """Проверка на комментирование постов неавторизованным
        пользовательем."""
        post = self.post
        comments_count = post.comments.all().count()
        form_data = {
            'text': 'Крутой коммент',
        }
        response = self.client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, '/auth/login/?next=/posts/1/comment/')
        self.assertEqual(post.comments.all().count(), comments_count)

    def test_comment_user(self):
        """Проверка на комментирование постов авторизованным пользовательем."""
        post = self.post
        comments_count = post.comments.all().count()
        form_data = {
            'text': 'Крутой коммент 2',
        }
        response = self.authorized_client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.pk}))
        self.assertEqual(post.comments.all().count(), comments_count + 1)
        self.assertEqual(post.comments.all()[0].text, form_data['text'])
