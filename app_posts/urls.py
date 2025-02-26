from django.urls import path

from . import views

app_name = 'posts'

urlpatterns = [
    path('me/', views.PersonalPostListApiView.as_view(), name='my-posts'),
    path('<slug:slug>/', views.PostRetrieveUpdateDestroyApiView.as_view(), name='detail'),
    path('', views.PostAPIView.as_view(), name='list'),
]
