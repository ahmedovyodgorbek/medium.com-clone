from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import PostsModel, PostTopicModel, PostCommentsModel

User = get_user_model()


class PostAuthorSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField(read_only=True)
    avatar = serializers.ImageField(source='profile.avatar', read_only=True)

    class Meta:
        model = User
        fields = ['full_name', 'avatar']

    @staticmethod
    def get_full_name(obj):
        return obj.get_full_name()


class PostModelSerializer(serializers.ModelSerializer):
    topics = serializers.PrimaryKeyRelatedField(
        queryset=PostTopicModel.objects.all(),
        many=True,
        required=False,
        write_only=True
    )
    claps_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = PostsModel
        fields = ['slug', 'image', 'body', 'title', 'short_description', 'topics',
                  'claps_count', 'comments_count', 'created_at']
        read_ony_fields = ['created_at', 'slug']

    @staticmethod
    def get_claps_count(obj):
        return obj.claps.count()

    @staticmethod
    def get_comments_count(obj):
        return obj.comments.count()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['author'] = PostAuthorSerializer(instance=instance.author).data
        return data


class PostClapsUserSerializer(serializers.ModelSerializer):
    short_bio = serializers.CharField(source='profile.short_bio')
    avatar = serializers.ImageField(source='profile.avatar')
    is_followed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['username', 'avatar', 'short_bio', 'is_followed']

    @staticmethod
    def get_is_followed(obj):
        return True


class PostCommentsSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    user = serializers.StringRelatedField()

    class Meta:
        model = PostCommentsModel
        fields = ['id', 'parent', 'comment', 'user', 'children']

    @staticmethod
    def get_children(obj):
        return obj.children.count()


class PostCommentClapsSerializer(serializers.Serializer):
    pass


class PostCommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = PostCommentsModel
        fields = ['comment', 'user']
        read_only_fields = ['user']
