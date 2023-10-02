from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.urls import reverse


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    author_rating = models.IntegerField(default=0, verbose_name='Рейтинг')

    class Meta:
        verbose_name = "Автор"
        verbose_name_plural = "Авторы"

    def __str__(self):
        return self.user.username

    def update_rating(self):
        author_posts_rating = Post.objects.filter(author_id=self.pk).aggregate(
            posts_rating_sum=Coalesce(Sum('post_rating') * 3, 0))
        author_comments_rating = Comment.objects.filter(user_id=self.user).aggregate(
            comments_rating_sum=Coalesce(Sum('comment_rating'), 0))
        author_post_comments_rating = Comment.objects.filter(post__author__user=self.user).aggregate(
            comments_rating_sum=Coalesce(Sum('comment_rating'), 0))

        self.author_rating = author_posts_rating['posts_rating_sum'] + author_comments_rating['comments_rating_sum'] + author_post_comments_rating['comments_rating_sum']
        self.save()


class Category(models.Model):
    category_name = models.CharField(max_length=25, unique=True, verbose_name='Название категории')
    subscribers = models.ManyToManyField(User, related_name='categories', verbose_name='Подписчики')

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.category_name


class Post(models.Model):
    article = 'AR'
    news = 'NW'
    SELECT_POST = [(article, 'article'), (news, 'news')]
    author = models.ForeignKey(Author, on_delete=models.CASCADE, verbose_name='Автор')
    post_type = models.CharField(max_length=2, choices=SELECT_POST, default=news, verbose_name='Тип публикации')
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')
    post_category = models.ManyToManyField(Category, through='PostCategory', verbose_name='Категории')
    post_title = models.CharField(max_length=255, verbose_name='Заголовок')
    post_text = models.TextField('Содержание')
    post_rating = models.IntegerField(default=0, verbose_name='Рейтинг')
    post_likes = models.ManyToManyField(User, blank=True, related_name='post_likes', verbose_name='Нравится')
    post_dislikes = models.ManyToManyField(User, blank=True, related_name='post_dislikes', verbose_name='Не нравится')

    class Meta:
        verbose_name = "Публикация"
        verbose_name_plural = "Публикации"

    def like(self):
        self.post_rating += 1
        self.save()

    def dislike(self):
        self.post_rating -= 1
        self.save()

    def preview(self):
        if len(f'{self.post_text}') > 124:
            return f'{self.post_text[:124]}...'
        return self.post_text

    def __str__(self):
        return self.post_title



class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, verbose_name='Публикация')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория')

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, verbose_name='Публикация')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    comment_text = models.CharField(max_length=255, verbose_name='Комментарий')
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name='Дата комментария')
    comment_rating = models.IntegerField(default=0, verbose_name='Рейтинг')
    comment_likes = models.ManyToManyField(User, blank=True, related_name='comment_likes', verbose_name='Нравится')
    comment_dislikes = models.ManyToManyField(User, blank=True, related_name='comment_dislikes', verbose_name='Не нравится')

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"

    def like(self):
        self.comment_rating += 1
        self.save()

    def dislike(self):
        self.comment_rating -= 1
        self.save()

    def __str__(self):
        return f'{self.user} ({self.comment_text[:30]}...)'

