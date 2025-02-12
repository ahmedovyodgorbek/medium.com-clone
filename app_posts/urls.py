from django.urls import path

from .views import PostAPIView, PostDetailAPIView

app_name = 'posts'

urlpatterns = [
    path('<slug:slug>/', PostDetailAPIView.as_view(), name='detail'),
    path('', PostAPIView.as_view(), name='list')
]
