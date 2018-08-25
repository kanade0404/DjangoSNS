from .forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic
from django.conf import settings
from sns.models import User
from django.http import Http404, HttpResponseBadRequest
from django.core.signing import BadSignature, SignatureExpired, loads, dumps
from django.shortcuts import redirect
from django.contrib.auth.backends import ModelBackend
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import get_template


# class SignUpView(generic.CreateView):
#     form_class = UserCreationForm
#     success_url = reverse_lazy('login')
#     template_name = 'accounts/signup.html'


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
    form_class = UserCreationForm

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.save()

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
    """ユーザー仮登録したよ"""
    template_name = 'accounts/signup_done.html'


class UserCreateComplete(generic.TemplateView):
    """メール内URLアクセス後のユーザー本登録"""
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
