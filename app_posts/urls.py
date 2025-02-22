from django.urls import path

from .import views

app_name = 'posts'

urlpatterns = [
    path('me/', views.PersonalPostListApiView.as_view(), name='my-posts'),
    path('<slug:slug>/', views.PostRetrieveUpdateDestroyApiView.as_view(), name='detail'),
    path('<slug:slug>/claps/', views.PostClapsAPIView.as_view(), name='claps'),
    # path('<slug:slug>/comments/', views.PostDetailAPIView.as_view(), name='comments'),
    # path('<slug:slug>/comments/claps', views.PostDetailAPIView.as_view(), name='comments-claps'),
    path('', views.PostAPIView.as_view(), name='list'),
]
