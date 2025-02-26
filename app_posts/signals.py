from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.text import slugify

from app_posts.models import PostsModel
from app_topics.models import PostTopicModel


@receiver(pre_save, sender=PostsModel)
def generate_slug_for_post(sender, instance, **kwargs):
    # Check if the post is new or the title has changed
    if instance.pk:  # Check if it's an existing object
        previous = PostsModel.objects.get(pk=instance.pk)
        # Only update the slug if the title has changed
        if previous.title == instance.title:
            return

    # Generate slug if post is new or title has changed
    original_slug = slugify(instance.title)
    slug = original_slug
    count = 1

    # Ensure slug uniqueness
    while PostsModel.objects.filter(slug=slug).exists():
        slug = f"{original_slug}-{count}"
        count += 1

    instance.slug = slug


@receiver(pre_save, sender=PostTopicModel)
def generate_slug_for_topic(sender, instance, **kwargs):
    # Check if the post is new or the title has changed
    if instance.pk:  # Check if it's an existing object
        previous = PostTopicModel.objects.get(pk=instance.pk)
        # Only update the slug if the title has changed
        if previous.title == instance.title:
            return

    # Generate slug if post is new or title has changed
    original_slug = slugify(instance.title)
    slug = original_slug
    count = 1

    # Ensure slug uniqueness
    while PostTopicModel.objects.filter(slug=slug).exists():
        slug = f"{original_slug}-{count}"
        count += 1

    instance.slug = slug
