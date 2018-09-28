from django.shortcuts import render, redirect
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from rest_framework import generics, status, mixins, viewsets, permissions, renderers
from rest_framework.decorators import api_view, detail_route
from rest_framework.response import Response
from rest_framework.reverse import reverse
from .models import Message, User
from .forms import SearchForm, MessageForm, UpdateUserForm
from .serializers import UserSerializer, MessageSerializer
from .permissions import IsOwnerOrReadOnly
import datetime


class UserViewSet(viewsets.ModelViewSet):
    """
    ユーザービュー
    """
    serializer_class = UserSerializer
    queryset = User.objects.filter(is_active=True)
    parser_classes = (permissions.IsAuthenticatedOrReadOnly,
                      IsOwnerOrReadOnly,)


class MessageViewSet(viewsets.ModelViewSet):
    """
    メッセージビュー
    """
    serializer_class = MessageSerializer
    queryset = Message.objects.filter(is_delete=False)
    filter_fields = ('user', 'is_delete')
    parser_classes = (permissions.IsAuthenticatedOrReadOnly,
                      IsOwnerOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        instance.is_delete = True
        instance.save()
        serializer = MessageSerializer(instance.data)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'users': reverse('user-list', request=request, format=format),
        'messages': reverse('message-list', request=request, format=format)
    })

# indexのビュー関数
# 一覧表示
# @login_required
# def index(request):
#     if request.method == 'GET':
#         messages = get_message()
#         serializer = MessageSerializer(messages, many=True)
#         return JsonResponse(serializer.data, safe=False)
#     elif request.method == 'POST':
#         data = JSONParser.parse(request)
#         serializer = MessageSerializer(data=data)
#         if serializer.is_valid():
#             try:
#                 serializer.save()
#             except:
#                 return HttpResponse(status=404)
#             return JsonResponse(serializer.data, status=201)
#         return JsonResponse(serializer.errors, status=400)
    # POST送信の場合
    # if request.method == 'POST':
    #     delete_search_condition_session(request)
    #     search_form = SearchForm()
    #     messages = get_message()
    # # GET送信の場合
    # else:
    #     search_form = SearchForm()
    #     if 'search_message' in request.session:
    #         search_form.search_message = request.session['search_message']
    #     if 'search_user' in request.session:
    #         search_form.search_user = request.session['search_user']
    #     if 'search_from_date' in request.session:
    #         search_form.search_from_date = request.session['search_from_date']
    #     if 'search_to_date' in request.session:
    #         search_form.search_to_date = request.session['search_to_date']
    #     # メッセージの取得
    #     messages = get_message()
    # params = {
    #     'login_user': request.user.username,
    #     'user_info': request.user,
    #     'contents': messages,
    #     'search_form': search_form,
    #     'message_form': MessageForm(),
    # }
    # return render(request, 'sns/index.html', params)
    # return render(request, 'sns/index.html', params)


# 投稿を取得
def get_message():
    messages = Message.objects.filter(is_delete=False).select_related()
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
            'login_user': request.user.username,
            'contents': get_message(),
            'search_form': SearchForm(),
            'message_form': message_form,
        }
    return redirect('sns:index')


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
    if not search_from_date == '':
        request.session['search_from_date'] = datetime.datetime.strptime(search_from_date, '%Y/%m/%d %H:%M:%S')
    if not search_to_date == '':
        request.session['search_to_date'] = datetime.datetime.strptime(search_to_date, '%Y/%m/%d %H:%M:%S')
    params = {
        'login_user': request.user.username,
        'contents': messages,
        'search_form': SearchForm(),
        'message_form': MessageForm(),
    }
    return redirect('sns:index')


# 投稿を削除する
@login_required
def delete_post(request):
    delete_message = Message.objects.filter(id=request.POST['id']).first()
    delete_message.is_delete = True
    delete_message.save()
    messages = get_message()
    params = {
        'login_user': request.user.username,
        'contents': messages,
        'search_form': SearchForm(),
        'message_form': MessageForm(),
    }
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


# ユーザー編集
# @login_required
class UpdateUserInfo(generic.UpdateView):
    model = User
    form_class = UpdateUserForm
    template_name = 'sns/user/user_info.html'

    def form_valid(self, form):
        user = form.save(commit=False)
        user.save()
        return redirect('sns:index')
