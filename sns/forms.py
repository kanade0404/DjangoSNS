from django import forms
from .models import Message, Group
from django.contrib.auth.models import User


# メッセージフォーム
class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['user', 'content', 'image']

    def __init__(self, *args, **kwargs):
        super(MessageForm, self).__init__(*args, **kwargs)
        self.fields['content'].widget.attrs.update({'rows': 4, 'cols': 40})
        self.fields['image'].required = False


# グループフォーム
class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['user', 'group_name']


# 検索フォーム
class SearchForm(forms.Form):
    search_message = forms.CharField(max_length=50, label='検索投稿', required=False)
    search_user = forms.CharField(max_length=50, label='検索ユーザー', required=False)
    search_from_date = forms.DateTimeField(label='投稿時間', widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    search_to_date = forms.DateTimeField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)


# グループのチェックボックスフォーム
class GroupCheckForm(forms.Form):
    def __init__(self, user, *args, **kwargs):
        super(GroupCheckForm, self).__init__(*args, **kwargs)
        public = User.objects.filter(username='public').first()
        self.fields['groups'] = forms.MultipleChoiceField(
            choices=[(item.group_name, item.group_name) for item in Group.objects.filter(owner__in=[user, public])],
            widget=forms.CheckboxSelectMultiple(),
        )


# グループの選択メニューホーム
class GroupSelectForm(forms.Form):
    def __init__(self, user, *args, **kwargs):
        super(GroupSelectForm, self).__init__(*args, **kwargs)
        self.fields['groups'] = forms.ChoiceField(
            choices=[('-', '-')] + [(item.group_name, item.group_name) for item in Group.objects.filter(owner=user)],
        )


# グループ作製フォーム
class CreateGroupForm(forms.Form):
    group_name = forms.CharField(max_length=50)


# 投稿フォーム
class PostForm(forms.Form):
    content = forms.CharField(max_length=200,
                              widget=forms.Textarea(attrs={'rows': 4, 'cols': 40}),
                              )
    image = forms.ImageField(required=False)

