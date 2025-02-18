import threading

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from app_users.serializers import LoginSerializer, RegisterSerializer, ConfirmEmailSerializer, ResendCodeSerializer
from .email import send_email_confirmation
from .models import ConfirmationCodesModel


class LoginApiView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data.get('user')
        tokens = user.get_tokens()

        return Response(data=tokens, status=status.HTTP_200_OK)


class RegisterApiView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        email_thread = threading.Thread(target=send_email_confirmation, args=(user,))
        email_thread.start()

        return Response(data={"detail": "Confirmation code has been sent to your email",
                              "data": serializer.data},
                        status=status.HTTP_201_CREATED)


class ConfirmEmailApiView(APIView):
    def post(self, request):
        serializer = ConfirmEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        ConfirmationCodesModel.objects.filter(user=user).delete()
        user.is_active = True
        tokens = user.get_tokens()
        user.save()
        return Response(data=tokens,
                        status=status.HTTP_200_OK)


class ResendCodeApiView(APIView):
    def post(self, request):
        serializer = ResendCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        email_thread = threading.Thread(target=send_email_confirmation, args=(user,))
        email_thread.start()

        return Response("Confirmation code has been sent to your email",
                        status=status.HTTP_200_OK)
