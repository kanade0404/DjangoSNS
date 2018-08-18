from django.db import models
from django.contrib.auth.models import User


class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='message_user', default=1)
    content = models.TextField(max_length=200)
    image = models.ImageField(upload_to='image/')
    share_id = models.IntegerField(default=-1)
    good_count = models.IntegerField(default=0)
    share_count = models.IntegerField(default=0)
    pub_date = models.DateTimeField(auto_now_add=True)
    is_delete = models.BooleanField(default=False)

    def __str__(self):
        return '{0}({1})'.format(self.content, self.user)

    def get_share(self):
        return Message.objects.get(id=self.share_id)

    class Meta:
        ordering = ('-pub_date',)


class Group(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_user', default=1)
    group_name = models.CharField(max_length=100)

    def __str__(self):
        return self.group_name


class Good(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='good_user', default=1)
    message = models.ForeignKey(Message, on_delete=models.CASCADE)

    def __str__(self):
        return 'good for {0}(by{1})'.format(self.message, self.user)
