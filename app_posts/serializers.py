from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import PostsModel, PostTopicModel, PostCommentsModel

User = get_user_model()


class PostAuthorSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(source='profile.avatar', read_only=True)

    class Meta:
        model = User
        fields = ['username', 'avatar']


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

    def get_is_followed(self, obj):
        user = self.context.get('user')
        return user.following.filter(to_user_id=obj.id).exists()


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


class PostTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostTopicModel
        fields = ['id', 'title', 'slug']
        read_only_fields = ['slug']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['author'] = PostAuthorSerializer(instance=instance.author).data
        return data
