from django.urls import path

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView, TokenBlacklistView,
)

from app_users.views import LoginApiView, RegisterApiView, ConfirmEmailApiView, ResendCodeApiView

app_name = 'users'

urlpatterns = [
    path('login/', LoginApiView.as_view(), name='login'),
    path('register/', RegisterApiView.as_view(), name='register'),
    path('logout/', TokenBlacklistView.as_view(), name='logout'),
    path('confirm/email/', ConfirmEmailApiView.as_view(), name='confirm-email'),
    path('resend/code/', ResendCodeApiView.as_view(), name='resend-code'),
    path('token/', TokenObtainPairView.as_view(), name='token'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
]
