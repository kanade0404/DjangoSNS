from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm, UserCreationForm
)
from sns.models import User


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attr['placeholder'] = field.label


class UserCreateForm(UserCreationForm):
    icon_image = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ('email', 'username', 'icon_image')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
