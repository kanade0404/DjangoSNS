from django.contrib import admin
from .models import Message, Group, Good

admin.site.register(Message)
# admin.site.register(Friend)
admin.site.register(Group)
admin.site.register(Good)
