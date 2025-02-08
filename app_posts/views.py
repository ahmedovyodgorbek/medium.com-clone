from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from app_posts.models import PostsModel
from .serializers import PostModelSerializer


@api_view(['GET', 'POST'])
def posts_view(request):
    if request.method == 'GET':
        posts = PostsModel.objects.all()
        serializer = PostModelSerializer(posts, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        serializer = PostModelSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
