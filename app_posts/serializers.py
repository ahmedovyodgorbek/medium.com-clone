from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import PostsModel

User = get_user_model()


class PostModelSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    slug = serializers.CharField(read_only=True)
    title = serializers.CharField()
    body = serializers.CharField(allow_blank=True)
    author = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    created_at = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        return PostsModel.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.body = validated_data.get('body', instance.body)
        instance.author = validated_data.get('author', instance.author)

        instance.save()
        return instance

    def validate_title(self, value):
        if len(value) > 50:
            raise serializers.ValidationError('the length of the title must be less than 50 characters !')
        return value

