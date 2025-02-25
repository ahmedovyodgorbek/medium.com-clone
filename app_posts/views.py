from django.contrib.auth import get_user_model
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListAPIView, ListCreateAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app_common.pagination import StandardResultsSetPagination, LargeResultsSetPagination
from app_common.permissions import IsOwnerOrReadOnly, IsCommentOwner
from app_posts.models import PostsModel, PostClapsModel, PostCommentsModel, PostCommentClapsModel, PostTopicModel
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


class CommentRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.PostCommentSerializer
    queryset = PostCommentsModel
    lookup_field = 'pk'
    permission_classes = [IsCommentOwner, IsAuthenticated]


class PostTopicListCreateAPIView(ListCreateAPIView):
    queryset = PostTopicModel.objects.all()
    pagination_class = LargeResultsSetPagination
    serializer_class = serializers.PostTopicSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PostTopicRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = PostTopicModel.objects.all()
    pagination_class = StandardResultsSetPagination
    serializer_class = serializers.PostTopicSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    lookup_field = 'slug'
