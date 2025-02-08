from rest_framework import serializers

from .models import PostsModel


class PostModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostsModel
        fields = '__all__'
