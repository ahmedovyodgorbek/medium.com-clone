from django.urls import path

from . import views

app_name = 'posts'

urlpatterns = [
    path('me/', views.PersonalPostListApiView.as_view(), name='my-posts'),
    path('<slug:slug>/', views.PostRetrieveUpdateDestroyApiView.as_view(), name='detail'),
    path('<slug:slug>/claps/', views.PostClapsAPIView.as_view(), name='post-claps'),
    path('<slug:slug>/comments/', views.PostCommentsListCreateAPIView.as_view(), name='comments'),
    path('comments/<int:pk>/', views.CommentChildrenListAPIView.as_view(), name='comments-children'),
    path('comment/update/<int:pk>/', views.CommentRetrieveUpdateDestroyAPIView.as_view(), name='comment-update'),
    path('comments/<int:pk>/claps/', views.CommentClapsListCreateAPIView.as_view(), name='comment-claps'),
    path('', views.PostAPIView.as_view(), name='list'),
]
