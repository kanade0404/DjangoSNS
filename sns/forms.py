from django import forms
from .models import Message, Group, Friend, Good
from django.contrib.auth.models import User


# メッセージフォーム
class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['owner', 'group', 'content']


# グループフォーム
class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['owner', 'group_name']


# フレンドフォーム
class FriendForm(forms.ModelForm):
    class Meta:
        model = Friend
        fields = ['owner', 'user', 'group']


# お気に入りフォーム
class GoodForm(forms.ModelForm):
    class Meta:
        model = Good
        fields = ['owner', 'message']


# 検索フォーム
class SearchForm(forms.Form):
    search = forms.CharField(max_length=100)


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
            choices=[('-', '-')] + [(item.user, item.user) for item in Group.objects.filter(owner=user)],
        )


# フレンドのチェックボックスフォーム
class FriendsForm(forms.Form):
    def __init__(self, user, friends=[], vals=[], *args, **kwargs):
        super(FriendsForm, self).__init__(*args, **kwargs)
        self.fields['friends'] = forms.MultipleChoiceField(
            choice=[(item.user, item.user) for item in friends],
            widget=forms.CheckboxSelectMultiple(),
            initial=vals
        )


# グループ作製フォーム
class CreateGroupForm(forms.Form):
    group_name = forms.CharField(max_length=50)


# 投稿フォーム
class PostForm(forms.Form):
    content = forms.CharField(max_length=200,
                              widget=forms.Textarea)

    def __init__(self, user, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        public = User.objects.filter(username='public').first()
        self.fields['groups'] = forms.ChoiceField(
            choices=[('-', '-')] + [(item.group_name, item.group_name)
                                    for item in Group.objects.first(owner__in=[user, public])]
        )
