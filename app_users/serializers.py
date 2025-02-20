from datetime import timedelta, datetime

from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.hashers import check_password
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from rest_framework import serializers

from app_users.models import ConfirmationCodesModel, OTPModel

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
        if now > expire_at:
            raise serializers.ValidationError("Confirmation code is expired")
        return attrs


class ResendCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()

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

        created_at = confirmation_code.created_at
        expire_at = created_at + timedelta(minutes=confirmation_code.minutes_to_expire)
        now = timezone.now()
        if now < expire_at:
            raise serializers.ValidationError("You have an active code")

        ConfirmationCodesModel.objects.filter(user=user).delete()
        return attrs


class RegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)
    first_name = serializers.CharField(max_length=128, required=False)
    last_name = serializers.CharField(max_length=128, required=False)

    class Meta:
        model = UserModel
        fields = ["first_name", "last_name", "username", "email", "password", "password2"]
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')

        if password != password2:
            raise serializers.ValidationError("Passwords do not match")
        validate_password(password=password)
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')

        user = UserModel.objects.create(**validated_data)
        user.set_password(validated_data['password'])
        user.is_active = False
        user.save()

        return user


class UserSerializer(serializers.ModelSerializer):
    short_bio = serializers.CharField(source='profile.short_bio')
    avatar = serializers.ImageField(source='profile.avatar')
    about = serializers.CharField(source='profile.about')
    pronouns = serializers.CharField(source='profile.pronouns')

    class Meta:
        model = UserModel
        fields = ['first_name', 'last_name', 'email', 'username',
                  'short_bio', 'avatar', 'about', 'pronouns']

    def update(self, instance, validated_data):
        profile = validated_data.pop('profile', {})

        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.username = validated_data.get('username', instance.username)
        instance.save()

        profile = instance.profile
        profile.short_bio = validated_data.get('short_bio', profile.short_bio)
        profile.avatar = validated_data.get('avatar', profile.avatar)
        profile.about = validated_data.get('about', profile.about)
        profile.pronouns = validated_data.get('pronouns', profile.pronouns)
        profile.save()
        return instance


class UpdatePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password1 = serializers.CharField(required=True)
    new_password2 = serializers.CharField(required=True)

    def validate(self, attrs):
        request = self.context.get('request')  # Get request object from context
        user = request.user  # Authenticated user

        old_password = attrs.get('old_password')
        new_password1 = attrs.get('new_password1')
        new_password2 = attrs.get('new_password2')

        if not user.check_password(old_password):
            raise serializers.ValidationError("Old password is incorrect")

        if new_password1 != new_password2:
            raise serializers.ValidationError("Passwords do not match")
        validate_password(new_password1, user=user)

        return attrs

    def save(self, **kwargs):
        request = self.context.get('request')
        user = request.user

        user.set_password(raw_password=self.validated_data['new_password1'])
        user.save()
        return user


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        email = attrs.get('email')
        try:
            user = UserModel.objects.get(email=email)
        except UserModel.DoesNotExist:
            raise serializers.ValidationError("Email is invalid")
        attrs['user'] = user
        return attrs


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    raw_password = serializers.CharField(max_length=18, write_only=True)
    new_password1 = serializers.CharField(max_length=18, write_only=True)
    new_password2 = serializers.CharField(max_length=18, write_only=True)

    def validate(self, attrs):
        email = attrs.pop('email')
        raw_password = attrs.pop('raw_password')
        new_password1 = attrs.pop('new_password1')
        new_password2 = attrs.pop('new_password2')

        try:
            user = UserModel.objects.get(email=email)
        except:
            raise serializers.ValidationError("Invalid Email")

        try:
            otp = OTPModel.objects.get(user=user)
            is_otp_valid = check_password(raw_password, otp.password)
        except OTPModel.DoesNotExist:
            raise serializers.ValidationError("Invalid or expired Password")

        if not (is_otp_valid and otp.is_valid()):
            otp.delete()
            raise serializers.ValidationError("Invalid or expired Password")
        otp.delete()

        if new_password1 != new_password2:
            raise serializers.ValidationError("Passwords do not match")
        validate_password(new_password1)

        attrs['new_password'] = new_password1
        attrs['user'] = user

        return attrs


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['username'] = user.username

        return token
