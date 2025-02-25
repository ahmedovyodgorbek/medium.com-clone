import threading

from django.contrib.auth import get_user_model
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.hashers import make_password
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app_users import serializers
from .email import send_email_confirmation, send_OTP
from .models import ConfirmationCodesModel, OTPModel, FollowModel
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


class FollowUserAPIView(APIView):
    serializer_class = serializers.FollowUserSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = dict()
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        from_user = request.user
        to_user = serializer.validated_data['to_user']
        if from_user == to_user:
            raise ValidationError("You cannot follow yourself")
        follow_status = FollowModel.objects.filter(from_user=from_user, to_user=to_user)
        if follow_status.exists():
            follow_status.first().delete()
            response['detail'] = f"User unfollowed {to_user}"
            response['status'] = "unfollowed"
            return Response(data=response, status=status.HTTP_204_NO_CONTENT)
        else:
            FollowModel.objects.create(from_user=from_user, to_user=to_user)
            response['detail'] = f"User started following {to_user}"
            response['status'] = "followed"
            return Response(data=response, status=status.HTTP_201_CREATED)

    def get_serializer(self, *args, **kwargs):
        return self.serializer_class(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        follow_type = request.query_params.get('type')
        if follow_type not in ['following', 'followers']:
            raise ValidationError("Invalid query params")

        if follow_type == 'following':
            users = UserModel.objects.filter(id__in=request.user.following.values_list('to_user_id', flat=True))
        else:
            users = UserModel.objects.filter(id__in=request.user.followers.values_list('from_user_id', flat=True))
        serializer = serializers.UserSerializer(users, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
