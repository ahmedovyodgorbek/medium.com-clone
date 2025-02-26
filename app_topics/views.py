from django.contrib.auth import get_user_model
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListAPIView, ListCreateAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from app_common.pagination import StandardResultsSetPagination, LargeResultsSetPagination
from app_common.permissions import IsOwnerOrReadOnly, IsCommentOwner
from app_posts.models import PostsModel, PostTopicModel
from . import serializers


class PostTopicListCreateAPIView(ListCreateAPIView):
    queryset = PostTopicModel.objects.all()
    pagination_class = LargeResultsSetPagination
    serializer_class = serializers.PostTopicSerializer
    permission_classes = [IsAuthenticated]


class PostTopicRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = PostTopicModel.objects.all()
    pagination_class = StandardResultsSetPagination
    serializer_class = serializers.PostTopicSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    lookup_field = 'slug'
