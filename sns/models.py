import re
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator, MinLengthValidator, ValidationError


class Message(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='message_owner')
    group = models.ForeignKey('Group', on_delete=models.CASCADE)
    content = models.TextField(max_length=200)
    share_id = models.IntegerField(default=-1)
    good_count = models.IntegerField(default=0)
    share_count = models.IntegerField(default=0)
    pub_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{0}({1})'.format(self.content, self.owner)

    def get_share(self):
        return Message.objects.get(id=self.share_id)

    class Meta:
        ordering = ('-pub_date',)


class Group(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_owner')
    group_name = models.CharField(max_length=100)

    def __str__(self):
        return self.group_name


class Friend(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friend_owner')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    def __str__(self):
        return '{0}({1})'.format(self.user, self.group)


class Good(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='good_owner')
    message = models.ForeignKey(Message, on_delete=models.CASCADE)

    def __str__(self):
        return 'good for {0}(by{1})'.format(self.message, self.owner)


def number_only(value):
    if re.match(r'^[0-9]*$', value) == None:
        raise ValidationError(
            '%(value)s is not Number',
            params={'value': value},
        )
