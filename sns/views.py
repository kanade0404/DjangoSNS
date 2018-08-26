from django.shortcuts import render
from .models import Message
from .forms import SearchForm, MessageForm
from django.contrib.auth.decorators import login_required


# indexのビュー関数
@login_required
def index(request):
    # POST送信の場合
    if request.method == 'POST':
        delete_search_condition_session(request)
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
        'login_user': request.user.username,
        'contents': messages,
        'search_form': search_form,
        'message_form': MessageForm(),
    }
    return render(request, 'sns/index.html', params)


# 投稿を取得
def get_message():
    # messages = Message.objects.filter(is_delete=False)
    messages = Message.objects.filter(is_delete=False).select_related()
    return messages


# 投稿を条件ありで取得（デフォルトは条件なしで取得）
def find_message(message, user, from_date, to_date):
    messages = Message.objects.filter(is_delete=False).select_related()
    if not message == '':
        messages = messages.filter(content__contains=message)
    if not user == '':
        messages = messages.filter(user__username=user)
    if not from_date == '':
        messages = messages.filter(pub_date__gt=from_date)
    if not to_date == '':
        messages = messages.filter(pub_date__gte=to_date)
    return messages


# 投稿を追加する
@login_required
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
        params = {
            'login_user': request.user,
            'contents': get_message(),
            'search_form': SearchForm(),
            'message_form': message_form,
        }
    finally:
        messages = get_message()
    params = {
        'login_user': request.user,
        'contents': messages,
        'search_form': SearchForm(),
        'message_form': MessageForm(),
    }
    return render(request, 'sns/index.html', params)


# 投稿を検索する
@login_required
def find_post(request):
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
    params = {
        'login_user': request.user,
        'contents': messages,
        'search_form': SearchForm(),
        'message_form': MessageForm(),
    }
    return render(request, 'sns/index.html', params)


# 投稿を削除する
@login_required
def delete_post(request):
    delete_message = Message.objects.filter(id=request.POST['id']).first()
    delete_message.is_delete = True
    delete_message.save()
    messages = get_message()
    params = {
        'login_user': request.user,
        'contents': messages,
        'search_form': SearchForm(),
        'message_form': MessageForm(),
    }
    return render(request, 'sns/index.html', params)


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
