from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from django.db import models

from app_common.models import BaseModel

UserModel = get_user_model()


class ProfileModel(BaseModel):
    user = models.OneToOneField(UserModel, models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='profile_images', null=True,
                               validators=[FileExtensionValidator(allowed_extensions=['jpg', 'png', 'gif'])])
    short_bio = models.CharField(max_length=255, null=True)
    about = models.TextField(null=True)
    pronouns = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = 'profile'
        verbose_name_plural = 'profiles'

