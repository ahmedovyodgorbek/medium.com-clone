import random
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.timezone import now
from rest_framework_simplejwt.tokens import RefreshToken

from app_common.models import BaseModel


class CustomUserModel(AbstractUser):
    email = models.EmailField(unique=True)

    def get_tokens(self):
        refresh = RefreshToken.for_user(self)
        refresh.set_exp(lifetime=timedelta(days=7))
        refresh.access_token.set_exp(lifetime=timedelta(days=1))

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }

    def get_confirmation_code(self, minutes_to_expire=2):
        """Generate a 6-digit confirmation code"""
        while True:
            code = random.randint(100000, 999999)  # 6-digit code
            user_code = ConfirmationCodesModel.objects.filter(user=self, code=code)
            if user_code.exists():
                user_code.delete()
            ConfirmationCodesModel.objects.create(
                user=self,
                code=code,
                minutes_to_expire=minutes_to_expire
            )
            return code


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


class ConfirmationCodesModel(BaseModel):
    code = models.PositiveSmallIntegerField(unique=True)
    user = models.OneToOneField(UserModel, models.CASCADE, related_name='confirmation_codes')
    minutes_to_expire = models.PositiveSmallIntegerField()

    def __str__(self):
        return f"{self.code} to {self.user.username}"

    class Meta:
        verbose_name = 'confirmation code'
        verbose_name_plural = 'confirmation codes'


class OTPModel(BaseModel):
    password = models.CharField(max_length=18)
    user = models.OneToOneField(UserModel, on_delete=models.CASCADE)

    def is_valid(self):
        return (now() - self.created_at).seconds < 180  # 2 minutes

    class Meta:
        verbose_name = 'OTP password'
        verbose_name_plural = 'OTP passwords'
