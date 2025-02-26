from django.urls import path

from . import views

app_name = 'comments'

urlpatterns = [
    path('comments/<int:pk>/', views.CommentChildrenListAPIView.as_view(), name='comments-children'),
    path('comment/update/<int:pk>/', views.CommentRetrieveUpdateDestroyAPIView.as_view(), name='comment-update'),
    path('<slug:slug>/comments/', views.PostCommentsListCreateAPIView.as_view(), name='comments'),
]
