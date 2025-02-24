import threading

from django.contrib.auth import get_user_model
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.hashers import make_password
from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app_users import serializers
from .email import send_email_confirmation, send_OTP
from .models import ConfirmationCodesModel, OTPModel
from .utils import generate_secure_password

UserModel = get_user_model()


class LoginApiView(APIView):
    permission_classes = [AllowAny]
    serializer_class = serializers.LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data.get('user')
        tokens = user.get_tokens()

        return Response(data=tokens, status=status.HTTP_200_OK)

    def get_serializer(self, *args, **kwargs):
        return self.serializer_class(*args, **kwargs)


class RegisterApiView(APIView):
    serializer_class = serializers.RegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        email_thread = threading.Thread(target=send_email_confirmation, args=(user,))
        email_thread.start()

        return Response(data={"detail": "Confirmation code has been sent to your email",
                              "data": serializer.data},
                        status=status.HTTP_201_CREATED)

    def get_serializer(self, *args, **kwargs):
        return self.serializer_class(*args, **kwargs)


class ConfirmEmailApiView(APIView):
    serializer_class = serializers.ConfirmEmailSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        ConfirmationCodesModel.objects.filter(user=user).delete()
        user.is_active = True
        tokens = user.get_tokens()
        user.save()
        return Response(data=tokens,
                        status=status.HTTP_200_OK)

    def get_serializer(self, *args, **kwargs):
        return self.serializer_class(*args, **kwargs)


class ResendCodeApiView(APIView):
    serializer_class = serializers.ResendCodeSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        email_thread = threading.Thread(target=send_email_confirmation, args=(user,))
        email_thread.start()

        return Response("Confirmation code has been sent to your email",
                        status=status.HTTP_200_OK)

    def get_serializer(self, *args, **kwargs):
        return self.serializer_class(*args, **kwargs)


class UserProfileApiView(RetrieveUpdateAPIView):
    serializer_class = serializers.UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user  # Ensure the current user is returned


class UpdatePasswordApiView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.UpdatePasswordSerializer

    def put(self, request):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response("Password has been updated successfully", status=status.HTTP_200_OK)

    def get_serializer(self, *args, **kwargs):
        return self.serializer_class(*args, **kwargs)


class ForgotPasswordApiView(APIView):
    serializer_class = serializers.EmailSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        raw_password = generate_secure_password()
        hashed_password = make_password(raw_password)
        print(raw_password)

        OTPModel.objects.create(password=hashed_password, user=user)

        threading.Thread(target=send_OTP, args=(user, raw_password)).start()

        return Response(data="Check your email for One Time Password", status=status.HTTP_200_OK)

    def get_serializer(self, *args, **kwargs):
        return self.serializer_class(*args, **kwargs)


class ResetPasswordApiView(APIView):
    serializer_class = serializers.ResetPasswordSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        new_password = serializer.validated_data['new_password']

        user.set_password(new_password)
        user.save()

        return Response(data="New password has been set", status=status.HTTP_200_OK)

    def get_serializer(self, *args, **kwargs):
        return self.serializer_class(*args, **kwargs)
