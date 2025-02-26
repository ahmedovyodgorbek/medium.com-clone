from django.urls import path

from . import views

app_name = 'claps'

urlpatterns = [
    path('comments/<int:pk>/claps/', views.CommentClapsListCreateAPIView.as_view(), name='comment-claps'),
    path('<slug:slug>/claps/', views.PostClapsAPIView.as_view(), name='post-claps'),

]
