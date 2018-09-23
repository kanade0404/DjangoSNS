from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm, UserCreationForm, PasswordResetForm, SetPasswordForm
)
from sns.models import User


class LoginForm(AuthenticationForm):
    """
    ログインフォーム
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label


class UserCreateForm(UserCreationForm):
    """
    ユーザー登録フォーム
    """
    icon_image = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ('email', 'username', 'icon_image')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label


class UserPasswordResetForm(PasswordResetForm):
    """
    パスワードを忘れた際のフォーム
    メールアドレスを入力して再設定画面に飛ぶ
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label


class UserSetPasswordForm(SetPasswordForm):
    """
    パスワードを再設定するフォーム
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label
