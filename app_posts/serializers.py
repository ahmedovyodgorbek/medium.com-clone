from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import PostsModel, PostTopicModel, PostCommentsModel

User = get_user_model()


class PostModelSerializer(serializers.ModelSerializer):
    topics = serializers.PrimaryKeyRelatedField(
        queryset=PostTopicModel.objects.all(),
        many=True,
        required=False
    )

    class Meta:
        model = PostsModel
        fields = "__all__"


class PostCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostCommentsModel
        fields = '__all__'

