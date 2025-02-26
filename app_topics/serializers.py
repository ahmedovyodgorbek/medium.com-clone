from django.contrib.auth import get_user_model
from rest_framework import serializers

from app_posts.models import PostTopicModel
from app_posts.serializers import PostAuthorSerializer

User = get_user_model()


class PostTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostTopicModel
        fields = ['id', 'title', 'slug']
        read_only_fields = ['slug']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['author'] = PostAuthorSerializer(instance=instance.author).data
        return data
