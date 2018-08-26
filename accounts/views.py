from .forms import UserCreateForm
from django.views import generic
from sns.models import User
from django.shortcuts import redirect
from django.contrib.auth.backends import ModelBackend


class UserAuth(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        email = username
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None


class UserCreate(generic.CreateView):
    template_name = 'accounts/signup.html'
    form_class = UserCreateForm

    def form_valid(self, form):
        user = form.save(commit=False)
        user.save()
        return redirect('accounts:signup_complete')


class UserCreateComplete(generic.TemplateView):
    """メール内URLアクセス後のユーザー本登録"""
    template_name = 'accounts/signup_complete.html'

    def get(self, request, **kwargs):
        return super().get(request, **kwargs)

