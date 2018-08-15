from rest_framework import serializers
from .models import Message, Photo


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ('id', 'content', 'good_count', 'share_count')


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ('image',)


class PostSerializer(serializers.Serializer):
    class Meta:
        message = Message
        photo = Photo
