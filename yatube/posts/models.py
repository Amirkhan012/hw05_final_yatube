from django.db import models
from django.contrib.auth import get_user_model

from core.models import CreatedModel


User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, null=True, max_length=200)
    description = models.TextField()

    def __str__(self):
        return self.title


class Post(CreatedModel, models.Model):
    text = models.TextField(
        verbose_name='Текст поста',
        help_text='Введите текст поста',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост',
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ('-pub_date', )

    def __str__(self):
        return self.text


class Comment(CreatedModel, models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария',
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Название поста',
    )
    text = models.TextField(
        max_length=500,
        verbose_name='Текст комментария',
    )

    class Meta:
        ordering = ('pub_date',)

    def __str__(self):
        return self.text


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='Нельзя подписываться дважды',
            ),
            models.CheckConstraint(
                check=~models.Q(author=models.F('user')),
                name='Нельзя подписываться на себя',
            )
        ]

    def __str__(self):
        return(
            f'{self.user.username} подписан на {self.author.username}'
        )
