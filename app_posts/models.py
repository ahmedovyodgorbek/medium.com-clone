from django.contrib.auth import get_user_model
from django.db import models

from app_common.models import BaseModel

UserModel = get_user_model()


class PostTopicModel(BaseModel):
    title = models.CharField(max_length=128)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'topic'
        verbose_name_plural = 'topics'


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


class PostClapsModel(BaseModel):
    user = models.ForeignKey(UserModel, on_delete=models.SET_NULL,
                             related_name='post_claps', null=True)
    post = models.ForeignKey(PostsModel, models.CASCADE, related_name='claps')

    def __str__(self):
        return f"post-{self.post.id} clapped by {self.user.username}"

    class Meta:
        verbose_name = 'post clap'
        verbose_name_plural = 'post claps'


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


class PostCommentClapsModel(BaseModel):
    user = models.ForeignKey(UserModel, on_delete=models.SET_NULL,
                             related_name='comment_claps', null=True)
    comment = models.ForeignKey(PostCommentsModel, models.CASCADE, related_name='claps')

    def __str__(self):
        return f"comment-{self.comment.id} clapped by {self.user.username}"

    class Meta:
        verbose_name = 'comment clap'
        verbose_name_plural = 'comment claps'
