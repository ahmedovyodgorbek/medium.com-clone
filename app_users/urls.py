from django.urls import path

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView, TokenBlacklistView,
)

from app_users import views

app_name = 'users'

urlpatterns = [
    path('login/', views.LoginApiView.as_view(), name='login'),
    path('register/', views.RegisterApiView.as_view(), name='register'),
    path('logout/', TokenBlacklistView.as_view(), name='logout'),
    path('me/', views.UserProfileApiView.as_view(), name='me'),
    path('confirm/email/', views.ConfirmEmailApiView.as_view(), name='confirm-email'),
    path('resend/code/', views.ResendCodeApiView.as_view(), name='resend-code'),
    path('update/password/', views.UpdatePasswordApiView.as_view(), name='update-password'),
    path('forgot/password/', views.ForgotPasswordApiView.as_view(), name='forgot-password'),
    path('reset/password/', views.ResetPasswordApiView.as_view(), name='reset-password'),
    path('token/', TokenObtainPairView.as_view(), name='token'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
]
