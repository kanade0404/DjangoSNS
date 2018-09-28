from rest_framework import serializers
from .models import User, Message


class UserSerializer(serializers.ModelSerializer):
    """
    ユーザーモデルシリアライザー
    """
    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'icon_image',
            'username'
        )

    def create(self, validate_data):
        return User.objects.create(**validate_data)

    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)
        instance.icon_image = validated_data.get('icon_image', instance.icon_image)
        instance.username = validated_data.get('username', instance.username)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()
        return instance


class MessageSerializer(serializers.ModelSerializer):
    """
    メッセージモデルシリアライザー
    """
    user = UserSerializer()

    class Meta:
        model = Message
        fields = (
            'id',
            'user',
            'content',
            'image',
            'pub_date'
        )

    def create(self, validated_data):
        return Message.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.content = validated_data.get('content', instance.content)
        instance.image = validated_data.get('image', instance.image)
        instance.is_delete = validated_data.get('is_delete', instance.is_delete)
        instance.save()
        return instance
