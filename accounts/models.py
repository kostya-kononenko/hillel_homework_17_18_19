from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.urls import reverse


class User(AbstractUser):

    def get_absolute_url(self):
        return reverse('authors-detail', args=[str(self.pk)])


class Post(models.Model):

    title = models.CharField(max_length=200)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    short_description = models.CharField(max_length=200)
    full_description = models.TextField()
    image = models.ImageField(upload_to='practical_work/media/post', blank=True)
    data_post = models.DateTimeField(default=timezone.now)
    published = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post-detail', args=[str(self.pk)])

    class Meta:
        ordering = ['title']


class Comment(models.Model):

    username = models.CharField(max_length=200, default='noname user')
    text_comment = models.TextField()
    posts = models.ForeignKey(Post, on_delete=models.CASCADE)
    published = models.BooleanField(default=False)

    def __str__(self):
        return self.text_comment

    def get_absolute_url(self):
        return reverse('comment-detail', args=[str(self.pk)])

    class Meta:
        ordering = ['text_comment']
        