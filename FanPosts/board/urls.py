from django.urls import path
from .views import *

urlpatterns = [
    path('ads/', PostsList.as_view(), name='post_list'),
    path('ad/<int:pk>/', (PostDetail.as_view()), name='post_detail'),
    path('ad/create/', PostCreate.as_view(), name='post_create'),
    path('ad/<int:pk>/edit/', PostUpdate.as_view(), name='post_edit'),
    path('ad/<int:pk>/delete/', PostDelete.as_view(), name='post_delete'),
    path('ads/user/<int:pk>/', UserPostsList.as_view(), name='user_posts_list'),
    path('ads/category/<int:pk>/', CategoryList.as_view(), name='category_list'),
    path('ads/category/<int:pk>/subscribe/', subscribe, name='subscribe'),
    path('ads/category/<int:pk>/unsubscribe/', unsubscribe, name='unsubscribe'),
    path('ad/<int:pk>/reply/create/', ReplyCreate.as_view(), name='reply_create'),
    path('ad/<int:pk>/replies/', RepliesPostList.as_view(), name='post_replies_list'),
    path('ad/reply/<int:pk>/', ReplyPostDetail.as_view(), name='post_reply_detail'),
    path('ad/reply/<int:pk>/accept/', AcceptReply.as_view(), name='reply_accept'),
    path('ad/reply/<int:pk>/delete/', ReplyDelete.as_view(), name='reply_delete'),
    path('ads/user/replies/', PostsUserReplies.as_view(), name='user_replies'),
]
