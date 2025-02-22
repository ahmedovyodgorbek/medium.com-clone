from django.contrib.auth import get_user_model
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app_common.pagination import StandardResultsSetPagination
from app_common.permissions import IsOwnerOrReadOnly
from app_posts.models import PostsModel, PostClapsModel
from . import serializers

UserModel = get_user_model()


class PostAPIView(APIView):
    serializer_class = serializers.PostModelSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request):
        posts = PostsModel.objects.all()

        paginator = self.pagination_class()
        paginated_posts = paginator.paginate_queryset(posts, request)
        serializer = self.serializer_class(paginated_posts, many=True)

        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def get_serializer(self, *args, **kwargs):
        return self.serializer_class(*args, **kwargs)


class PostDetailAPIView(APIView):
    serializer_class = serializers.PostModelSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get(self, request, slug):
        post = self.get_object(slug=slug)
        serializer = self.serializer_class(post)
        return Response({
            "success": True,
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def put(self, request, slug):
        post = self.get_object(slug=slug)
        self.check_object_permissions(request, post)

        serializer = serializers.PostModelSerializer(post, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(data={
                "success": True,
                "data": serializer.data
            }, status=status.HTTP_202_ACCEPTED)

        return Response(data={
            "success": False,
            "detail": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, slug):
        post = self.get_object(slug=slug)
        self.check_object_permissions(request, post)
        serializer = serializers.PostModelSerializer(post, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(data={
                "success": True,
                "data": serializer.data
            }, status=status.HTTP_202_ACCEPTED)

        return Response(data={
            "success": False,
            "detail": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, slug):
        post = self.get_object(slug=slug)
        self.check_object_permissions(request, post)
        post.delete()
        return Response(data={
            "success": True,
            "detail": "Post is deleted"
        }, status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def get_object(slug):
        try:
            return PostsModel.objects.get(slug=slug)
        except PostsModel.DoesNotExist:
            raise NotFound({
                "success": False,
                "detail": "Post was not found"
            })

    def get_serializer(self, *args, **kwargs):
        return self.serializer_class(*args, **kwargs)


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
        serializer = self.serializer_class(paginated_users, many=True)

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
