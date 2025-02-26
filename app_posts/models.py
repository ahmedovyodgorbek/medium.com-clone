from django.contrib.auth import get_user_model
from django.db import models

from app_common.models import BaseModel
from app_topics.models import PostTopicModel

UserModel = get_user_model()


class PostsModel(BaseModel):
    author = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='posts')
    slug = models.SlugField(unique=True, null=True)
    title = models.CharField(max_length=255)
    body = models.TextField()
    short_description = models.CharField(max_length=255)
    image = models.ImageField(upload_to='post_image')

    topics = models.ManyToManyField(PostTopicModel, related_name='posts')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'post'
        verbose_name_plural = 'posts'
