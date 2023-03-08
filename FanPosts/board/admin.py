from django.contrib import admin
from .models import *
from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget


class PostAdminForm(forms.ModelForm):
    post_content = forms.CharField(widget=CKEditorUploadingWidget())

    class Meta:
        model = Post
        fields = '__all__'


class PostAdmin(admin.ModelAdmin):
    list_display = ('post_title', 'id', 'author', 'post_category', 'date_creation', 'post_content')
    form = PostAdminForm


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name', 'id')


class ReplyAdmin(admin.ModelAdmin):
    list_display = ('reply_text', 'id', 'user', 'date_creation', 'reply_accept', 'post')


class OneTimeCodeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'code')


admin.site.register(Category, CategoryAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Reply, ReplyAdmin)
admin.site.register(OneTimeCode, OneTimeCodeAdmin)
