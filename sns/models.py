from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.base_user import BaseUserManager
from django.core.mail import send_mail
from KanadeSns import settings


class UserManager(BaseUserManager):
    """
    ユーザー管理モデル
    """
    user_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Super must have is_superuser=True')
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    ユーザーモデル
    """
    # メールアドレス
    email = models.EmailField(_('email'), unique=True)
    # ユーザーアイコン画像
    icon_image = models.ImageField(upload_to='icon/', blank=True)
    # ユーザー名
    username = models.CharField(_('username'), max_length=50)
    # 管理者フラグ
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_(
            'Designates whether the user can log into this admin site.'),
    )
    # アクティブフラグ（論理削除）
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be threaded as active.'
            'Unselect this instead of deleting accounts.'
        ),
    )
    # 登録日時（YYYY-MM-DD hh:mm:ss）
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __repr__(self):
        return '{}: {}'.format(self.pk, self.username)

    # メール送信
    def email_user(self, subject, message, from_email=settings.EMAIL_HOST_USER, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)


class Message(models.Model):
    """
    メッセージモデル
    """
    # ユーザーモデル
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='message_user', default=1)
    # メッセージ内容
    content = models.TextField(max_length=200)
    # 投稿画像
    image = models.ImageField(upload_to='image/', blank=True)
    # シェアのID
    share_id = models.IntegerField(default=-1)
    # 被お気に入り数
    good_count = models.IntegerField(default=0)
    # 被シェア数
    share_count = models.IntegerField(default=0)
    # 投稿時間
    pub_date = models.DateTimeField(auto_now_add=True)
    # 投稿削除（論理削除）
    is_delete = models.BooleanField(default=False)

    def __str__(self):
        return '{0}({1})'.format(self.content, self.user)

    def get_share(self):
        return Message.objects.get(id=self.share_id)

    class Meta:
        ordering = ('-pub_date',)


class Group(models.Model):
    """
    グループモデル
    """
    # ユーザーモデル
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_user', default=1)
    # グループ名
    group_name = models.CharField(max_length=100)

    def __str__(self):
        return self.group_name


class Good(models.Model):
    """
    お気に入りモデル
    """
    # ユーザーモデル
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='good_user', default=1)
    # メッセージモデル
    message = models.ForeignKey(Message, on_delete=models.CASCADE)

    def __str__(self):
        return 'good for {0}(by{1})'.format(self.message, self.user)
