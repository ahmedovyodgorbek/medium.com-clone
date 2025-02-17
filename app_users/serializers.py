from datetime import timedelta, datetime

from django.contrib.auth import get_user_model, authenticate
from django.utils import timezone
from rest_framework import serializers

from app_users.models import ConfirmationCodesModel

UserModel = get_user_model()

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class LoginSerializer(serializers.Serializer):
    email_or_username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        email_or_username = attrs.get('email_or_username')
        password = attrs.get('password')

        try:
            user = UserModel.objects.get(username=email_or_username)
        except:
            user = UserModel.objects.get(email=email_or_username)

        if user is None:
            raise serializers.ValidationError({
                "success": False,
                "detail": "User was not found with this username or email"
            })

        authenticated_user = authenticate(username=user.username, password=password)
        if authenticated_user is None:
            raise serializers.ValidationError({
                "success": False,
                "detail": "Username(email) or password is invalid"
            })

        attrs["user"] = authenticated_user
        return attrs


class ConfirmEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.IntegerField()

    def validate(self, attrs):
        try:
            user = UserModel.objects.get(email=attrs['email'])
            confirmation_code = ConfirmationCodesModel.objects.get(user=user)
            attrs['user'] = user
        except UserModel.DoesNotExist:
            raise serializers.ValidationError({
                "success": False,
                "detail": "User with this email does not exist"
            })
        except ConfirmationCodesModel.DoesNotExist:
            raise serializers.ValidationError({
                "success": False,
                "detail": "Invalid confirmation code"
            })

        created_at = confirmation_code.created_at
        expire_at = created_at + timedelta(minutes=confirmation_code.minutes_to_expire)
        now = timezone.now()
        if expire_at < now:
            raise serializers.ValidationError({
                "success": False,
                "detail": "Confirmation code is expired"
            })

        return attrs


class RegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = UserModel
        fields = ["first_name", "last_name", "username", "email", "password", "password2"]
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({
                "success": False,
                "detail": "Passwords do not match"
            })
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')

        user = UserModel(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            username=validated_data['username'],
            email=validated_data['email'],
        )
        user.set_password(validated_data['password'])
        user.is_active = False
        user.save()

        return user


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['username'] = user.username
        token['email'] = user.email

        return token
