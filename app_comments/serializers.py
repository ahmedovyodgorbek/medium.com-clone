from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import PostCommentsModel

User = get_user_model()


class PostCommentsSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    user = serializers.StringRelatedField()

    class Meta:
        model = PostCommentsModel
        fields = ['id', 'parent', 'comment', 'user', 'children']
        read_only_fields = ['id']

    @staticmethod
    def get_children(obj):
        return obj.children.count()


class PostCommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = PostCommentsModel
        fields = ['comment', 'user']
        read_only_fields = ['user']
