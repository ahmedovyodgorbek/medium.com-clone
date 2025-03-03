from django.contrib.auth import get_user_model
from django.db import models

from app_common.models import BaseModel
from app_posts.models import PostsModel

UserModel = get_user_model()


class PostCommentsModel(BaseModel):
    user = models.ForeignKey(UserModel, on_delete=models.SET_NULL,
                             related_name='post_comments', null=True)
    post = models.ForeignKey(PostsModel, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', blank=True, null=True,
                               on_delete=models.CASCADE, related_name='children')

    comment = models.TextField()

    def __str__(self):
        return f"{self.user.username} commented on {self.post.id}: {self.comment}"

    class Meta:
        verbose_name = 'post comment'
        verbose_name_plural = 'post comments'
