from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Message, User
from .forms import SearchForm, MessageForm, UpdateUserForm
import datetime


# 一覧表示
@login_required
def index(request):
    # GET送信の場合
    if request.method == 'GET':
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
            'login_user': request.user.username,
            'user_info': request.user,
            'contents': messages,
            'search_form': search_form,
            'message_form': MessageForm(),
        }
        return render(request, 'sns/index.html', params)
    # POST送信の場合
    elif request.method == 'POST':
        delete_search_condition_session(request)
        add_post(request)
        params = {
            'login_user': request.user.username,
            'user_info': request.user,
            'contents': get_message(),
            'search_form': SearchForm(),
            'message_form': MessageForm(),
        }
        return render(request, 'sns/index.html', params)


# 投稿を全件取得
def get_message():
    messages = Message.objects.filter(is_delete=False).select_related()
    return messages


# 投稿検索
def get_fast_message(request):
    messages = Message.objects.filter(is_delete=False).filter(content__contains=request['message'])
    return messages


# 投稿を条件ありで取得（デフォルトは条件なしで取得）
def find_message(request):
    messages = Message.objects.filter(is_delete=False).select_related()
    if not request['message'] == '':
        messages = messages.filter(content__contains=request['message'])
    if not request['user'] == '':
        messages = messages.filter(user__username=request['user'])
    if not request['from_date'] == '':
        messages = messages.filter(pub_date__gt=request['from_date'])
    if not request['to_date'] == '':
        messages = messages.filter(pub_date__gte=request['to_date'])
    return messages


# 投稿を追加する
def add_post(request):
    message_form = MessageForm(request.POST, request.FILES)
    if not message_form.is_valid():
        raise ValueError('invalid form')
    msg = Message()
    msg.user = request.user
    msg.content = request.POST['content']
    msg.image = message_form.cleaned_data['image']
    try:
        msg.save()
    except Exception as e:
        print(e)


# 投稿を検索する
@login_required
def find_post(request):
    search_form = SearchForm(request.POST)
    search_message = request.POST['search_message']
    search_user = request.POST['search_user']
    search_from_date = request.POST['search_from_date']
    search_to_date = request.POST['search_to_date']
    messages = find_message(search_message)
    # セッションに格納
    request.session['search_message'] = search_message
    request.session['search_user'] = search_user
    if not search_from_date == '':
        request.session['search_from_date'] = datetime.datetime.strptime(search_from_date, '%Y/%m/%d %H:%M:%S')
    if not search_to_date == '':
        request.session['search_to_date'] = datetime.datetime.strptime(search_to_date, '%Y/%m/%d %H:%M:%S')
    return redirect('sns:index')


# 投稿を削除する
@login_required
def delete_post(request):
    delete_message = Message.objects.filter(id=request.POST['id']).first()
    delete_message.is_delete = True
    delete_message.save()
    return redirect('sns:index')


# 検索情報のセッションを削除する
def delete_search_condition_session(request):
    if 'search_message' in request.session:
        del request.session['search_message']
    if 'search_user' in request.session:
        del request.session['search_user']
    if 'search_from_date' in request.session:
        del request.session['search_from_date']
    if 'search_to_date' in request.session:
        del request.session['search_to_date']


# ユーザー情報表示
@login_required
def user_detail(request, pk):
    # GETならユーザー情報取得
    if request.method == 'GET':
        try:
            user = get_user(pk)
        except User.DoesNotExist:
            pass
        except User.MultipleObjectsReturned:
            pass
    # POSTならユーザー情報更新
    elif request.method == 'POST':
        try:
            request.user.save()
        except:
            return None
    params = {
        'login_user': request.user.username,
        'user_info': get_user(pk),
        'form': UpdateUserForm(),
    }
    return render(request, 'sns/user/user_info.html', params)


# ユーザー情報取得
def get_user(user_id):
    user = User.objects.filter(is_active=True).get(pk=user_id)
    return user
