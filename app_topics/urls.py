from django.urls import path

from . import views

app_name = 'posts'

urlpatterns = [
    path('topics/', views.PostTopicListCreateAPIView.as_view(), name='topics'),
    path('topic/<slug:slug>/', views.PostTopicRetrieveUpdateDestroyAPIView.as_view(), name='detail')
]
