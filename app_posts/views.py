from django.contrib.auth import get_user_model
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListAPIView, ListCreateAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from app_common.pagination import StandardResultsSetPagination
from app_common.permissions import IsOwnerOrReadOnly
from app_posts.models import PostsModel
from . import serializers

UserModel = get_user_model()


class PostAPIView(ListCreateAPIView):
    queryset = PostsModel.objects.all()
    serializer_class = serializers.PostModelSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PostRetrieveUpdateDestroyApiView(RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.PostModelSerializer
    queryset = PostsModel.objects.all()
    lookup_field = 'slug'
    permission_classes = [IsOwnerOrReadOnly]


class PersonalPostListApiView(ListAPIView):
    serializer_class = serializers.PostModelSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PostsModel.objects.filter(author=self.request.user).order_by('-id')
