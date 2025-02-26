from django.contrib.auth import get_user_model
from rest_framework.generics import ListCreateAPIView, get_object_or_404, ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated

from app_common.pagination import StandardResultsSetPagination
from app_common.permissions import IsCommentOwner
from app_posts.models import PostsModel
from . import serializers
from .models import PostCommentsModel

UserModel = get_user_model()


class PostCommentsListCreateAPIView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    serializer_class = serializers.PostCommentsSerializer

    def get_queryset(self):
        post = get_object_or_404(PostsModel, slug=self.kwargs['slug'])
        return PostCommentsModel.objects.filter(post=post, parent__isnull=True).order_by('-id')

    def perform_create(self, serializer):
        post = get_object_or_404(PostsModel, slug=self.kwargs['slug'])
        return serializer.save(post=post, user=self.request.user)


class CommentChildrenListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    serializer_class = serializers.PostCommentsSerializer

    def get_queryset(self):
        comment = get_object_or_404(PostCommentsModel, id=self.kwargs['pk'])
        return PostCommentsModel.objects.filter(parent=comment).order_by('-id')


class CommentRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.PostCommentSerializer
    queryset = PostCommentsModel
    lookup_field = 'pk'
    permission_classes = [IsCommentOwner, IsAuthenticated]
