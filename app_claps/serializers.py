from django.contrib.auth import get_user_model
from rest_framework import serializers

from . import models

User = get_user_model()


class PostClapsUserSerializer(serializers.ModelSerializer):
    short_bio = serializers.CharField(source='profile.short_bio')
    avatar = serializers.ImageField(source='profile.avatar')
    is_followed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['username', 'avatar', 'short_bio', 'is_followed']

    def get_is_followed(self, obj):
        user = self.context.get('user')
        return user.following.filter(to_user_id=obj.id).exists()


class PostCommentClapsSerializer(serializers.Serializer):
    pass
