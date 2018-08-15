import sys
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Message, Group, Good, Photo
from .forms import GroupCheckForm, GroupSelectForm, SearchForm, CreateGroupForm, PostForm
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets
from rest_framework.response import Response
from .serializer import MessageSerializer, PhotoSerializer


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all().select_related()
    serializer_class = MessageSerializer

# indexのビュー関数
@login_required
def index(request):
    post_form = PostForm()
    # POST送信の場合
    if request.method == 'POST':
        # 検索の場合
        if request.POST['mode'] == '__search_form__':
            search_form = SearchForm(request.POST)
            search_message = request.POST['search_message']
            search_user = request.POST['search_user']
            search_from_date = request.POST['search_from_date']
            search_to_date = request.POST['search_to_date']
            messages = find_message(search_message, search_user, search_from_date, search_to_date)
            # セッションに格納
            request.session['search_message'] = search_message
            request.session['search_user'] = search_user
            request.session['search_from_date'] = search_from_date
            request.session['search_to_date'] = search_to_date
        # 投稿の場合
        elif request.POST['mode'] == '__post_form__':
            search_form = SearchForm()
            post_form = PostForm(request.POST, request.FILES)
            if not post_form.is_valid():
                raise ValueError('invalid form')
            # グループの取得
            # (pub_user, group) = get_public()
            # メッセージを作成し設定して保存
            msg = Message()
            msg.user = request.user
            msg.content = request.POST['content']
            photo = Photo()
            photo.image = post_form.cleaned_data['image']
            photo.user = request.user
            try:
                msg.save()
                photo.save()
            except Exception as e:
                print(e)
                params = {
                    'login_user': request.user,
                    'contents': get_message(),
                    'search_form': search_form,
                    'post_form': post_form,
                }
            finally:
                messages = get_message()

        else:
            search_form = SearchForm()
            messages = get_message()
    # GET送信の場合
    else:
        search_form = SearchForm()
        if 'search_message' in request.session:
            search_form.search_message = request.session['search_message']
        if 'search_user' in request.session:
            search_form.search_user = request.session['search_user']
        if 'search_from_date' in request.session:
            search_form.search_from_date = request.session['search_from_date']
        if 'search_to_date' in request.session:
            search_form.search_to_date = request.session['search_to_date']
        # メッセージの取得
        messages = get_message()
    params = {
        'login_user': request.user,
        'contents': messages,
        'search_form': search_form,
        'post_form': post_form,
    }
    return render(request, 'sns/index.html', params)


# グループの作成処理
@login_required
def create_group(request):
    # グループを作りユーザーとグループ名を設定して保存する
    gp = Group()
    gp.user = request.user
    gp.group_name = request.POST['group_name']
    gp.save()
    messages.info(request, '新しいグループを作成しました')
    return redirect(to='/sns/group')


# メッセージのポスト処理
# @login_required
# def post(request):
#     # POST送信の処理
#     if request.method == 'POST':
#         # 送信内容の取得
#         gr_name = request.POST['groups']
#         content = request.POST['content']
#         # グループの取得
#         group = Group.objects.filter(owner=request.user).filter(group_name=gr_name).first()
#         if group == None:
#             (pub_user, group) = get_public()
#         # メッセージを作成し設定して保存
#         msg = Message()
#         msg.user = request.user
#         msg.group = group
#         msg.content = content
#         msg.save()
#         messages.success(request, '新しいメッセージを投稿しました。')
#         return redirect(to='/sns')
#     # GETアクセス時の処理
#     else:
#         form = PostForm(request.user)
#     # 共通処理
#     params = {
#         'login_user': request.user,
#         'form': form,
#     }
#     return render(request, 'sns/post.html', params)


# 投稿を100件まで条件なしで取得
def get_message():
    messages = Message.objects.select_related().all()
    return messages


# 投稿を条件ありで取得（デフォルトは条件なしで100件まで取得）
def find_message(message, user, from_date, to_date):
    messages = Message.objects.select_related().all()
    if not message == '':
        messages = messages.filter(content__contains=message)
    if not user == '':
        messages = messages.filter(user__username=user)
    if not from_date == '':
        messages = messages.filter(pub_date__gt=from_date)
    if not to_date == '':
        messages = messages.filter(pub_date__gte=to_date)
    return messages


# def get_public():
#     public_user = User.objects.filter(username='public').first()
#     public_group = Group.objects.filter(user_id=public_user.id).first()
#     return (public_user, public_group)
