from django import forms
from .models import *


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['post_title', 'post_content', 'post_category']
        labels = {
            'post_title': 'Заголовок',
            'post_content': 'Содержание',
            'post_category': 'Категория',
        }
        widgets = {
            'post_title': forms.Textarea(attrs={'class': 'form-text', 'cols': 70, 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.fields['post_category'].empty_label = 'Выберите категорию'


class ReplyForm(forms.ModelForm):
    class Meta:
        model = Reply
        fields = ['reply_text']
        labels = {
            'reply_text': 'Введите текст отклика',
        }
        widgets = {
            'reply_text': forms.Textarea(attrs={'class': 'form-text', 'cols': 100, 'rows': 7}),
        }
