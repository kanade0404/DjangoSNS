from .forms import UserCreateForm, LoginForm
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from sns.models import User
from django.shortcuts import redirect
from django.contrib.auth.backends import ModelBackend
from django.template.loader import get_template
from django.core.signing import BadSignature, SignatureExpired, loads, dumps
from django.conf import settings
from django.http import Http404, HttpResponseBadRequest


class UserAuth(ModelBackend, LoginView):
    """
    ユーザー認証
    """
    template_name = 'registration/login.html'
    form_class = LoginForm

    def authenticate(self, request, username=None, password=None, **kwargs):
        email = username
        try:
            user = User.objects.filter(email=email).filter(is_active=True).get()
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None


class Logout(LoginRequiredMixin, LogoutView):
    """
    ログアウトページ遷移
    """
    template_name = 'registration/logged_out.html'


class UserCreate(generic.CreateView):
    """
    ユーザー登録
    """
    template_name = 'accounts/signup.html'
    form_class = UserCreateForm

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.save()
        # アクティベーションURLの送付処理
        current_site = get_current_site(self.request)
        domain = current_site.domain
        context = {
            'protocol': 'https' if self.request.is_secure() else 'http',
            'domain': domain,
            'token': dumps(user.pk),
            'user': user,
        }
        subject_template = get_template('accounts/mail_template/signup/subject.txt')
        subject = subject_template.render(context)
        message_template = get_template('accounts/mail_template/signup/message.txt')
        message = message_template.render(context)
        user.email_user(subject, message)
        return redirect('accounts:signup_done')


class UserCreateDone(generic.TemplateView):
    template_name = 'accounts/signup_done.html'


class UserCreateComplete(generic.TemplateView):
    """
    メール内URLアクセス後のユーザー本登録
    """
    template_name = 'accounts/signup_complete.html'
    timeout_seconds = getattr(settings, 'ACTIVATION_TIMEOUT_SECONDS', 60 * 60 * 24)  # デフォルトでは1日以内

    def get(self, request, **kwargs):
        """tokenが正しければ本登録."""
        token = kwargs.get('token')
        try:
            user_pk = loads(token, max_age=self.timeout_seconds)
        # 期限切れ
        except SignatureExpired:
            return HttpResponseBadRequest()
        # tokenが間違っている
        except BadSignature:
            return HttpResponseBadRequest()
        # tokenは問題なし
        else:
            try:
                user = User.objects.get(pk=user_pk)
            except User.DoesNotExist:
                return HttpResponseBadRequest()
            else:
                if not user.is_active:
                    # 問題なければ本登録とする
                    user.is_active = True
                    user.save()
                    return super().get(request, **kwargs)

        return HttpResponseBadRequest()
