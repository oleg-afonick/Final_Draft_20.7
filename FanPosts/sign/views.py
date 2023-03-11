from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from board.filters import PostFilter
from .forms import BaseRegisterForm, UserForm
from django.shortcuts import redirect, render
from board.models import *
from django.core.mail import send_mail
from FanPosts import settings
from string import hexdigits
import random


class BaseRegisterView(CreateView):
    model = User
    template_name = 'sign/signup.html'
    form_class = BaseRegisterForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = BaseRegisterForm()
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            active = form.save(commit=False)
            active.is_active = False
            active.save()
        return redirect('code', request.POST['username'])


class GetCode(CreateView):
    template_name = 'sign/code.html'

    def get_context_data(self, **kwargs):
        if not OneTimeCode.objects.filter(user=self.kwargs.get('user')).exists():
            code = ''.join(random.sample(hexdigits, 5))
            OneTimeCode.objects.create(user=self.kwargs.get('user'), code=code)
            user = User.objects.get(username=self.kwargs.get('user'))
            send_mail(
                subject=f'Код активации',
                message=f'Код активации аккаунта: {code}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
            )

    def post(self, request, *args, **kwargs):
        if 'code' in request.POST:
            user = request.path.split('/')[-1]
            if OneTimeCode.objects.filter(code=request.POST['code'], user=user).exists():
                User.objects.filter(username=user).update(is_active=True)
                OneTimeCode.objects.filter(code=request.POST['code'], user=user).delete()
            else:
                return render(self.request, 'sign/invalid_code.html')
        return redirect('login')


class Profile(LoginRequiredMixin, TemplateView):
    template_name = 'sign/profile.html'

    def get_context_data(self, **kwargs):
        queryset = Reply.objects.filter(post__author_id=self.request.user.pk).order_by('-date_creation')
        context = super().get_context_data(**kwargs)
        context['filter'] = PostFilter(self.request.GET, queryset, request=self.request.user.pk)
        return context


class ProfileDetail(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'sign/profile_detail.html'
    context_object_name = 'user'


class ProfileUpdate(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = 'sign/profile_update.html'
    context_object_name = 'user'
    success_url = '/sign/profile/'

    def dispatch(self, request, *args, **kwargs):
        user = self.get_object()
        if user != self.request.user:
            return render(self.request, 'sign/403.html')
        return super(ProfileUpdate, self).dispatch(request, *args, **kwargs)


class ProfileDelete(LoginRequiredMixin, DeleteView):
    model = User
    template_name = 'sign/profile_delete.html'
    success_url = '/'

    def dispatch(self, request, *args, **kwargs):
        user = self.get_object()
        if user != self.request.user:
            return render(self.request, 'sign/403.html')
        return super(ProfileDelete, self).dispatch(request, *args, **kwargs)
