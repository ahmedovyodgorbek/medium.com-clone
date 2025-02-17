import threading

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from app_users.serializers import LoginSerializer, RegisterSerializer, ConfirmEmailSerializer
from app_users.utils import get_tokens_for_user
from .email import send_email_confirmation
from .models import ConfirmationCodesModel


class LoginApiView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data.get('user')
        tokens = get_tokens_for_user(user)

        return Response(data=tokens, status=status.HTTP_200_OK)


class RegisterApiView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            email_thread = threading.Thread(target=send_email_confirmation, args=(user,))
            email_thread.start()

            return Response(data={"success": True,
                                  "detail": "Confirmation code has been sent to your email",
                                  "data": serializer.data},
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConfirmEmailApiView(APIView):
    def post(self, request):
        serializer = ConfirmEmailSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            ConfirmationCodesModel.objects.filter(user=user).delete()
            user.is_active = True
            user.save()
            return Response({
                "success": True,
                "detail": "Your email has been confirmed"
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
