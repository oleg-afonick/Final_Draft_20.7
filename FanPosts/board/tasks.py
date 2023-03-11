from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from .models import Post, Category
import datetime


@shared_task
def send_email_task(pk):
    post = Post.objects.get(pk=pk)
    category = post.post_category
    title = post.post_title
    subscribers_emails = []
    subscribers_users = category.subscribers.all()
    for sub_user in subscribers_users:
        subscribers_emails.append(sub_user.email)
    html_content = render_to_string(
        'post_created_email.html',
        {
            'text': title,
            'link': f'{settings.SITE_URL}/board/ad/{pk}',
            'category': category,
        }
    )

    msg = EmailMultiAlternatives(
        subject=f'Новое объявление в категории "{post.post_category}"',
        body='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=subscribers_emails,
    )

    msg.attach_alternative(html_content, 'text/html')
    msg.send()

