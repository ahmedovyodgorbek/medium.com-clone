from django.contrib.auth import get_user_model
from django.db import models

from app_common.models import BaseModel

UserModel = get_user_model()


class PostTopicModel(BaseModel):
    title = models.CharField(max_length=128)
    slug = models.SlugField(unique=True, null=True)
    author = models.ForeignKey(UserModel, models.CASCADE, related_name='created_topics')

    def __str__(self):
        return f"{self.title} by {self.author.username}"

    class Meta:
        verbose_name = 'topic'
        verbose_name_plural = 'topics'


class FollowTopicModel(BaseModel):
    user = models.ForeignKey(UserModel, models.CASCADE, related_name='topics')
    topics = models.ManyToManyField(PostTopicModel, related_name='followers')

    class Meta:
        verbose_name = 'topic follower'
        verbose_name_plural = 'topic followers'
