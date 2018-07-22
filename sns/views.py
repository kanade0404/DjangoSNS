from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator

from .models import Message, Friend, Group, Good
from .forms import GroupCheckForm, GroupSelectForm, SearchForm, FriendsForm, CreateGroupForm, PostForm

from django.db.models import Q
from django.contrib.auth.decorators import login_required


# indexのビュー関数
@login_required(login_url='/admin/login')
def index(request):
    # publicのユーザーを取得
    (public_user, public_group) = get_public()
    if request.method == 'POST':
        if request.POST['mode'] == '__check_form__':
            # フォームの作成
            search_form = SearchForm()
            check_form = GroupCheckForm(request.user, request.POST)
            # チェックされたグループ名をリストに入れる
            glist = []
            for item in request.POST.getlist('groups'):
                glist.append(item)
            # メッセージの取得
            messages = get_your_group_message(request.user, glist, None)
        # Groupsメニューを変更した時の処理
        if request.POST['mode'] == '__search_form__':
            # フォームの用意
            search_form = SearchForm(request.POST)
            check_form = GroupCheckForm(request.user)
            # グループのリストを取得
            gps = Group.objects.filter(owner=request.user)
            glist = [public_group]
            for item in gps:
                glist.append(item)
            # メッセージの取得
            messages = get_your_group_message(request.user, glist, request.POST['search'])
    else:
        # フォームの用意
        search_form = SearchForm()
        check_form = GroupCheckForm(request.user)
        # グループのリストを取得
        gps = Group.objects.filter(owner=request.user)
        glist = [public_group]
        for item in gps:
            glist.append(item)
        # メッセージの取得
        messages = get_your_group_message(request.user, glist, None)
    params = {
        'login_user': request.user,
        'contents': messages,
        'check_form': check_form,
        'search_form': search_form,
    }
    return render(request, 'sns/index.html', params)


@login_required(login_url='/admin/login')
def groups(request):
    # 自分が登録したフレンドを取得
    friends = Friend.objects.filter()
    # POST送信時の処理
    if request.method == 'POST':
        # Groupメニュー選択肢の処理
        if request.POST['mode'] == '__groups_form__':
            # 選択肢たグループ名を取得
            sel_group = request.POST['groups']
            # グループを取得
            gp = Group.objects.filter(owner=request.user).filter(group_name=sel_group).first()
            # Groupに含まれるフレンドを取得
            fds = Group.objects.filter(owner=request.user).filter(group=gp)
            # 全てのフレンドにグループを設定し保存する
            vlist = []
            for item in fds:
                vlist.append(item.user.username)
            # フォームの用意
            group_form = GroupSelectForm(request.user, request.POST)
            friends_form = FriendsForm(request.user, friends=friends, vals=vlist)
        # フレンドのチェック更新時の処理
        if request.POST['mode'] == '__friends_form__':
            # 選択したグループの取得
            sel_group = request.POST['group']
            group_obj = Group.objects.filter(group_name=sel_group).first()
            # チェックしたフレンドを取得
            sel_fds = request.POST.getlist('friends')
            # フレンドのユーザーを取得
            sel_users = User.objects.filter(username__in=sel_fds)
            # ユーザーのリストに含まれるユーザーが登録したフレンドを取得
            fds = Friend.objects.filter(owner=request.user).filter(user__in=sel_users)
            # 全てのフレンドにグループを設定し保存する
            vlist = []
            for item in fds:
                item.group = group_obj
                item.save()
                vlist.append(item.user.username)
            # メッセージを設定
            messages.success(request, 'チェックされたFriendを{0}に登録しました'.format(sel_group))
            # フォームを用意
            group_form = GroupSelectForm(request.user, {'groups':sel_group})
            friends_form = FriendsForm(request.user, friends=friends, vals=vlist)
    # GETアクセス時の処理
    else:
        # フォームの用意
        groups_form = GroupSelectForm(request.user)
        friends_form = FriendsForm(request.user, friends=friends, vals=[])
        sel_group = '-'
    # 共通処理
    create_form = CreateGroupForm()
    params = {
        'login_user': request.user,
        'groups_user': groups_form,
        'friends_form': friends_form,
        'create_form': create_form,
        'group': sel_group,
    }
    return render(request, 'sns/groups.html')


# フレンドの追加処理
@login_required(login_url='/admin/login/')
def add(request):
    # 追加するユーザーを取得
    add_name = request.GET['name']
    add_user = User.objects.filter(username=add_name).first()
    # ユーザーが本人だった場合の処理
    if add_user == request.user:
        messages.info(request, '自分自身をフレンドに追加することはできません')
        return redirect(to='/sns')
    # publicの取得
    (public_user, public_group) = get_public()
    # add_userのフレンドの数を調べる
    frd_num = Friend.objects.filter(owner=request.user).filter(user=add_user).count()
    # ゼロより大きければ既に登録ずみ
    if frd_num > 0:
        messages.info(request, '{0}は既に追加されています'.format(add_user.username))
        return redirect(to='/sns')
    # 以下フレンドの登録処理
    frd = Friend()
    frd.owner = request.user
    frd.user = add_user
    frd.group = public_group
    frd.save()
    # メッセージを設定
    messages.success(request, '{0}を追加しました。groupページに移動して、追加したフレンドをメンバーに設定してください。'.format(add_user.username))
    return redirect(to='/sns')


# グループの作成処理
@login_required(login_url='/admin/login')
def create_group(request):
    # グループを作りユーザーとグループ名を設定して保存する
    gp = Group()
    gp.owner = request.user
    gp.group_name = request.POST['group_name']
    gp.save()
    messages.info(request, '新しいグループを作成しました')
    return redirect(to='/sns/group')


# メッセージのポスト処理
@login_required(login_url='/admin/login')
def post(request):
    # POST送信の処理
    if request.method == 'POST':
        # 送信内容の取得
        gr_name = request.POST['groups']
        content = request.POST['content']
        # グループの取得
        group = Group.objects.filter(owner=request.user).filter(group_name=gr_name).first()
        if group == None:
            (pub_user, group) = get_public()
        # メッセージを作成し設定して保存
        msg = Message()
        msg.owner = request.user
        msg.group = group
        msg.content = content
        msg.save()
        messages.success(request, '新しいメッセージを投稿しました。')
        return redirect(to='/sns')
    # GETアクセス時の処理
    else:
        form = PostForm(request.user)
    # 共通処理
    params = {
        'login_user': request.user,
        'form': form,
    }
    return render(request, 'sns/post.html', params)


# 投稿をシェアする
@login_required(login_url='/admin/login')
def share(request, share_id):
    # シェアするメッセージの取得
    share = Message.objects.get(id=share_id)
    # POST送信時の処理
    if request.method == 'POST':
        # 送信内容の取得
        gr_name = request.POST['groups']
        content = request.POST['content']
        # グループの取得
        group = Group.objects.filter(owner=request.user).filter(group_name=gr_name).first()
        if group == None:
            (pub_user, group) = get_public()
        # メッセージを作成し設定して保存
        msg = Message()
        msg.owner = request.user
        msg.group = group
        msg.content = content
        msg.share_id = share.id
        msg.save()
        share_msg = msg.get_share()
        share_msg.share_count += 1
        share_msg.save()
        # メッセージを設定
        messages.success(request, 'メッセージをシェアしました')
        return redirect(to='/sns')
    # 共通処理
    form = PostForm(request.user)
    params = {
        'login_user': request.user,
        'form': form,
        'share': share,
    }
    return render(request, 'sns/share.html', params)


# いいねボタンの処理
@login_required(login_url='/admin/login')
def good(request, good_id):
    # いいねするメッセージを取得
    good_msg = Message.objects.get(id=good_id)
    # 自分がメッセージにいいねした数を調べる
    is_good = Good.objects.filter(owner=request.user).filter(message=good_msg).count()
    # ゼロより大きければいいね済み
    if is_good > 0:
        messages.success(request, '既にメッセージはいいねしています')
        return redirect(to='/sns')
    # メッセージのいいねカウントを一つ増やす
    good_msg.good_count += 1
    good_msg.save()
    # いいねを作成し設定して保存
    good = Good()
    good.owner = request.user
    good.message = good_msg
    good.save()
    # メッセージを設定
    messages.success(request, 'メッセージにいいねしました')
    return redirect(to='/sns')


def get_your_group_message(owner, glist, find):
    (public_user, public_group) = get_public()
    groups = Group.objects.filter(Q(owner=owner)|Q(owner=public_user)).filter(group_name=glist)
    me_friends = Friend.objects.filter(group__in=groups)
    me_users = []
    for f in me_friends:
        me_users.append(f.user)
    his_groups = Group.objects.filter(owner__in=me_users)
    his_friends = Friend.objects.filter(user=owner).filter(group__in=his_groups)
    me_groups = []
    for hf in his_friends:
        me_groups.append(hf.group)
    if find == None:
        messages = Message.objects.filter(Q(group__in=groups)|Q(group__in=me_groups))[:100]
    else:
        messages = Message.objects.filter(Q(group__in=groups)|Q(group__in=me_groups)).filter(content__contains=find)[:100]
    return messages


def get_public():
    public_user = User.objects.filter(username='public').first()
    public_group = Group.objects.filter(owner=public_user).first()
    return (public_user, public_group)
