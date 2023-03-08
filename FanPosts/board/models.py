from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField
from django.urls import reverse


class Category(models.Model):
    category_name = models.CharField(max_length=64, unique=True)
    subscribers = models.ManyToManyField(User, related_name='categories')

    def __str__(self):
        return self.category_name


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post_title = models.CharField(max_length=256)
    post_content = RichTextField()
    post_category = models.ForeignKey(Category, on_delete=models.CASCADE)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.post_title

    def get_replies_post(self):
        replies = []
        replies_post = Reply.objects.filter(post_id=self.pk)
        for reply in replies_post:
            replies.append(reply.text)
        return replies

    def get_absolute_url(self):
        return reverse('post_detail', args=[str(self.id)])


class Reply(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reply_text = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)
    reply_accept = models.BooleanField(default=False)

    def get_posts_reply(self):
        posts = []
        posts_reply = Post.objects.filter(pk=self.post_id)
        for post in posts_reply:
            posts.append(post.post_title)
        return posts

    def get_category(self):
        category = Post.objects.get(pk=self.post_id).post_category
        return category

    def __str__(self):
        return f'{self.user} ({self.reply_text[:30]}...)'

    def get_absolute_url(self):
        return reverse('post_reply_detail', args=[str(self.pk)])


class OneTimeCode(models.Model):
    user = models.CharField(max_length=256)
    code = models.CharField(max_length=10)
