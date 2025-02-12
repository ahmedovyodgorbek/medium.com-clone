from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import PostsModel, PostTopicModel

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
