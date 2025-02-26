from django.contrib.auth import get_user_model
from django.db import models

from app_comments.models import PostCommentsModel
from app_common.models import BaseModel
from app_posts.models import PostsModel

UserModel = get_user_model()


# Create your models here.
class PostClapsModel(BaseModel):
    user = models.ForeignKey(UserModel, on_delete=models.SET_NULL,
                             related_name='post_claps', null=True)
    post = models.ForeignKey(PostsModel, models.CASCADE, related_name='claps')

    def __str__(self):
        return f"post-{self.post.id} clapped by {self.user.username}"

    class Meta:
        verbose_name = 'post clap'
        verbose_name_plural = 'post claps'


class PostCommentClapsModel(BaseModel):
    user = models.ForeignKey(UserModel, on_delete=models.SET_NULL,
                             related_name='comment_claps', null=True)
    comment = models.ForeignKey(PostCommentsModel, models.CASCADE, related_name='claps')

    def __str__(self):
        return f"comment-{self.comment.id} clapped by {self.user.username}"

    class Meta:
        verbose_name = 'comment clap'
        verbose_name_plural = 'comment claps'
