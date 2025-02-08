from django.urls import path

from .views import posts_view

app_name = 'posts'

urlpatterns = [
    path('', posts_view, name='list')
]
