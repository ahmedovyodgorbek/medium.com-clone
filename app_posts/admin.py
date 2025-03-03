from django.contrib import admin

from . import models

admin.site.register(models.PostsModel)
admin.site.register(models.PostTopicModel)
