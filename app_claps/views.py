from django.contrib.auth import get_user_model
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.generics import ListCreateAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app_comments.models import PostCommentsModel
from app_common.pagination import StandardResultsSetPagination
from app_posts.models import PostsModel
from . import serializers
from .models import PostCommentClapsModel, PostClapsModel

UserModel = get_user_model()


class PostClapsAPIView(APIView):
    serializer_class = serializers.PostClapsUserSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get(self, request, slug):
        post = self.get_object(slug=slug)
        claps = PostClapsModel.objects.filter(post=post)
        claps_count = claps.count()
        # get rid of dublicated users
        users_list = claps.values_list('user', flat=True).distinct()
        users_count = users_list.count()
        # get user objects using their ids
        user_objects = UserModel.objects.filter(id__in=users_list).order_by('-id')

        paginator = self.pagination_class()
        paginated_users = paginator.paginate_queryset(user_objects, request)
        serializer = self.serializer_class(paginated_users, many=True, context={"user": request.user})

        return Response(data={
            "claps_count": claps_count,
            "users_count": users_count,
            "users": serializer.data
        }, status=status.HTTP_200_OK)

    def post(self, request, slug):
        post = self.get_object(slug=slug)
        user = request.user

        PostClapsModel.objects.create(user=user, post=post)
        claps_count = self.get_claps_count(post=post)
        return Response(data={"claps_count": claps_count}, status=status.HTTP_201_CREATED)

    def get_claps_count(self, post):
        return PostClapsModel.objects.filter(user=self.request.user, post=post).count()

    @staticmethod
    def get_object(slug):
        try:
            return PostsModel.objects.get(slug=slug)
        except PostsModel.DoesNotExist:
            raise ValidationError('Post does not exist')

    def get_serializer(self, *args, **kwargs):
        return self.serializer_class(*args, **kwargs)


class CommentClapsListCreateAPIView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    serializer_class = serializers.PostClapsUserSerializer

    def create(self, request, *args, **kwargs):
        comment = get_object_or_404(PostCommentsModel, id=self.kwargs['pk'])
        PostCommentClapsModel.objects.create(
            user=self.request.user, comment=comment
        )
        claps_count = PostCommentClapsModel.objects.filter(user=self.request.user, comment=comment).count()

        return Response(data={"claps_count": claps_count}, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        comment = get_object_or_404(PostCommentsModel, id=self.kwargs['pk'])

        claps = PostCommentClapsModel.objects.filter(comment=comment)
        claps_count = claps.count()

        user_ids = claps.values_list('user_id', flat=True).distinct()
        users = UserModel.objects.filter(id__in=user_ids).order_by('-id')

        page = self.paginate_queryset(users)
        if page is not None:
            serializer = self.serializer_class(page, many=True)
        else:
            serializer = self.serializer_class(page, many=True)
        return Response({
            "claps_count": claps_count,
            "users_count": users.count(),
            "users": serializer.data
        })

    def get_queryset(self):
        """Django requires this, so we return a dummy queryset."""
        return PostCommentClapsModel.objects.none()  # Empty queryset
