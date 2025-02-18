from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import ProfileModel

UserModel = get_user_model()


@receiver(post_save, sender=UserModel)
def create_profile(sender, instance, **kwargs):
    ProfileModel.objects.get_or_create(user=instance)
