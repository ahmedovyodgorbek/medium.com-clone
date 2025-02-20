from django.contrib import admin

from app_users.models import CustomUserModel, ProfileModel, ConfirmationCodesModel, OTPModel

admin.site.register(CustomUserModel)
admin.site.register(ProfileModel)
admin.site.register(ConfirmationCodesModel)
admin.site.register(OTPModel)