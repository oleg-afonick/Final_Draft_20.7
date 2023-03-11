from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.core.mail import send_mail
from FanPosts import settings
from .filters import PostFilter
from .models import *
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from .forms import PostForm, ReplyForm
from django.contrib.auth.mixins import LoginRequiredMixin
from .tasks import send_email_task


def home(request):
    return render(request, 'home.html')


def main(request):
    categories = Category.objects.all()
    context = {'categories': categories}
    return render(request, 'main.html', context=context)


class PostsList(ListView):
    model = Post
    ordering = '-date_creation'
    template_name = 'posts.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


class PostDetail(DetailView):
    model = Post
    template_name = 'post.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.post = get_object_or_404(Post, id=self.kwargs['pk'])
        replies = Reply.objects.filter(post_id=self.kwargs['pk'])
        context['categories'] = Category.objects.all()
        context['replies'] = replies
        return context


class PostCreate(LoginRequiredMixin, CreateView):
    form_class = PostForm
    model = Post
    template_name = 'post_create.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        if self.request.method == 'POST':
            form.instance.author = self.request.user
        post.save()
        send_email_task.delay(post.pk)
        return super().form_valid(form)


class PostUpdate(LoginRequiredMixin, UpdateView):
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'

    def dispatch(self, request, *args, **kwargs):
        post = self.get_object()
        context = {'post_id': post.pk}
        if post.author != self.request.user:
            return render(self.request, 'post_lock.html', context=context)
        return super(PostUpdate, self).dispatch(request, *args, **kwargs)


class PostDelete(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('post_list')

    def dispatch(self, request, *args, **kwargs):
        post = self.get_object()
        context = {'post_id': post.pk}
        if post.author != self.request.user:
            return render(self.request, 'post_lock.html', context=context)
        return super(PostDelete, self).dispatch(request, *args, **kwargs)


class UserPostsList(ListView):
    model = Post
    template_name = 'user_posts_list.html'
    context_object_name = 'user_posts_list'
    paginate_by = 10

    def get_queryset(self):
        self.user = get_object_or_404(User, id=self.kwargs['pk'])
        queryset = Post.objects.filter(author=self.user).order_by('-date_creation')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.user
        return context


class CategoryList(ListView):
    model = Category
    template_name = 'category_list.html'
    context_object_name = 'category_posts_list'
    paginate_by = 10

    def get_queryset(self):
        self.post_category = get_object_or_404(Category, id=self.kwargs['pk'])
        queryset = Post.objects.filter(post_category=self.post_category).order_by('-date_creation')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_subscriber'] = self.request.user not in self.post_category.subscribers.all()
        context['is_subscriber'] = self.request.user in self.post_category.subscribers.all()
        context['categories'] = Category.objects.all()
        context['category'] = self.post_category
        return context


@login_required
def subscribe(request, pk):
    user = request.user
    category = Category.objects.get(id=pk)
    category.subscribers.add(user)
    return redirect(f'/board/ads/category/{category.pk}')


@login_required
def unsubscribe(request, pk):
    user = request.user
    category = Category.objects.get(id=pk)
    category.subscribers.remove(user)
    return redirect(f'/board/ads/category/{category.pk}')


class ReplyCreate(LoginRequiredMixin, CreateView):
    form_class = ReplyForm
    model = Reply
    template_name = 'reply_create.html'

    def form_valid(self, form):
        reply = form.save(commit=False)
        self.post = get_object_or_404(Post, id=self.kwargs['pk'])
        form.instance.user = self.request.user
        form.instance.post = self.post
        reply.save()
        post = Post.objects.get(pk=self.kwargs.get('pk'))
        author = User.objects.get(pk=post.author_id)
        send_mail(
            subject=f'Отклик на объявление!',
            message=f'На ваше объявление: "{post}" был оставлен отклик: "{reply.reply_text}" пользователем {self.request.user}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[author.email],
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = get_object_or_404(Post, id=self.kwargs['pk'])
        context['post'] = post
        return context


class RepliesPostList(ListView):
    model = Reply
    ordering = '-date_creation'
    template_name = 'replies_post_list.html'
    context_object_name = 'replies_post'
    paginate_by = 10

    def get_queryset(self):
        self.post = get_object_or_404(Post, id=self.kwargs['pk'])
        queryset = Reply.objects.filter(post=self.post).order_by('-date_creation')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = self.post
        return context


class ReplyPostDetail(DetailView):
    model = Reply
    template_name = 'post_reply.html'
    context_object_name = 'reply'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.reply = get_object_or_404(Reply, id=self.kwargs['pk'])
        post = Post.objects.get(id=self.reply.post_id)
        context['post'] = post
        context['reply'] = self.reply
        return context

    def dispatch(self, request, *args, **kwargs):
        self.reply = get_object_or_404(Reply, id=self.kwargs['pk'])
        post = Post.objects.get(id=self.reply.post_id)
        context = {'post_id': post.pk}
        if not self.reply.reply_accept and self.reply.user != self.request.user and post.author != self.request.user:
            return render(self.request, 'reply_lock.html', context=context)
        return super(ReplyPostDetail, self).dispatch(request, *args, **kwargs)


class AcceptReply(LoginRequiredMixin, TemplateView):
    template_name = 'reply_accept.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        reply_id = self.kwargs.get('pk')
        reply = Reply.objects.get(pk=reply_id)
        user = User.objects.get(id=reply.user_id)
        post = Post.objects.get(id=reply.post_id)
        context['reply'] = reply
        context['user'] = user
        context['post'] = post
        if not reply.reply_accept:
            send_mail(
                subject=f'Ваш отклик принят!',
                message=f'Ваш отклик: "{reply.reply_text}" был принят пользователем {self.request.user}!',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
            )
        Reply.objects.filter(pk=reply_id).update(reply_accept=True)
        return context

    def dispatch(self, request, *args, **kwargs):
        self.reply = get_object_or_404(Reply, id=self.kwargs['pk'])
        post = Post.objects.get(id=self.reply.post_id)
        if post.author != self.request.user:
            return render(self.request, 'accept_lock.html')
        return super(AcceptReply, self).dispatch(request, *args, **kwargs)


class ReplyDelete(LoginRequiredMixin, DeleteView):
    model = Reply
    template_name = 'reply_delete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        reply = get_object_or_404(Reply, id=self.kwargs['pk'])
        context['post'] = reply.post
        return context

    def dispatch(self, request, *args, **kwargs):
        reply = self.get_object()
        context = {'reply': reply}
        if reply.post.author != self.request.user:
            return render(self.request, 'reply_delete_lock.html', context=context)
        return super(ReplyDelete, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('post_replies_list', kwargs={'pk': self.object.post.pk})


class PostsUserReplies(LoginRequiredMixin, ListView):
    model = Reply
    template_name = 'posts_user_replies.html'
    context_object_name = 'replies'

    def get_context_data(self, **kwargs):
        queryset = Reply.objects.filter(post__author_id=self.request.user.pk).order_by('-date_creation')
        context = super().get_context_data(**kwargs)
        context['filter'] = PostFilter(self.request.GET, queryset, request=self.request.user.pk)
        return context
