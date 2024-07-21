##-import libraries-##
from datetime import datetime, timezone
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.hashers import make_password
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions, serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import Token

# from django.db import transaction
from .enums import TokenEnum

# from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from .util import is_valid_email, generate_otp
from .tasks import send_account_verification_email, send_password_reset_email, send_password_reset_email_otp_to_email

##--imports from the model class-##
from .models import User, PendingUser, Token


##--create the user serializer--##
class ObtainTokenSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        access_token = refresh.access_token
        self.user.save_last_login()
        data["refresh"] = str(refresh)
        data["access"] = str(access_token)
        return data

    @classmethod
    def get_token(cls, user: User) -> Token:
        if user.is_flagged:
            raise exceptions.AuthenticationFailed(
                _("Contact Admin"), code="authentication"
            )
        token = super().get_token(user)
        token.id = user.id
        token["first_name"] = user.first_name
        token["email"] = user.email
        return token


class AuthTokenSerializer(serializers.Serializer):
    """This serializer is for user authentication"""

    email = serializers.CharField()
    password = serializers.CharField(
        style={"input_type": "password"}, trim_whitespace=False
    )

    def validate(self, attrs):
        """Validate and authenticate the user"""
        email = attrs.get("email")
        password = attrs.get("password")
        if email:
            user = authenticate(
                request=self.context.get("request"),
                username=email.lower().strip(),
                password=password,
            )
        if not user:
            message = _("Unable to authenticate")
            raise serializers.ValidationError(message, code="authentication")
        attrs["user"] = user
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    new_password_1 = serializers.CharField(
        max_length=120, write_only=True, required=True, min_length=6
    )
    old_password = serializers.CharField(
        max_length=120, write_only=True, required=True, min_length=6
    )


    def validate_old_password(self, value):
        user_request = self.context["request"].user
        if not user_request.check_password(value):
            raise serializers.ValidationError(
                {"old_password": "Old password is not correct"}
            )
        return value

    def save(self):
        user: User = self.context["request"].user
        new_password_1 = self.validated_data["new_password_1"]
        user.set_password(new_password_1)
        user.save(update_fields=["password"])


##-- This serializer creates a password from the reset OTP serializer--##
class CreatePasswordFromChangedOTPSerializer(serializers.Serializer):
    otp = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class AccountVerificationSerializer(serializers.Serializer):
    otp = serializers.CharField(required=True)
    email = serializers.EmailField(required=True, allow_blank=False)

    def validate(self, attrs: dict):
        email_address: str = attrs.get("email").strip().lower()
        pending_user: PendingUser = PendingUser.objects.filter(
            email=email_address, verification_code=attrs.get("otp")
        ).first()
        if pending_user and pending_user.is_valid():
            attrs["email"] = email_address
            attrs["password"] = pending_user.password
            attrs["pending_user"] = pending_user

        else:
            raise serializers.ValidationError(
                {"otp": "Verification failed. OTP is Invalid"}
            )
        return super().validate(attrs)

    def create(self, validated_data: dict):
        validated_data.pop("otp")
        pending_user = validated_data.pop("pending_user")
        User.objects.create_user_with_email(**validated_data)
        pending_user.delete()
        return validated_data


##--- Email Serializer---##
class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


##-- Serializer to reset password--##
class InitiatePasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, allow_blank=False)

    def validate(self, attrs):
        email = attrs.get("email")
        strip_email = email.lower().strip()
        user = get_user_model().objects.filter(email=strip_email, is_active=True).first()
        if not user:
            raise serializers.ValidationError({"email": "Email number not registered"})
        attrs["email"] = strip_email
        attrs["user"] = user
        return super().validate(attrs)

    def create(self, validated_data):
        email = validated_data.get("email")
        user = validated_data.get("user")
        otp = generate_otp()
        token, _ = Token.objects.update_or_create(
            user=user,
            token_type=TokenEnum.PASSWORD_RESET,
            defaults={
                "user": user,
                "token_type": TokenEnum.PASSWORD_RESET,
                "token": otp,
                "created_at": datetime.now(timezone.utc),
            },
        )

        message_info = {
            "otp": otp,
            "email": email,
        }
        send_password_reset_email.delay(message_info)
        return token


class ListUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = [
            "id",
            "first_name",
            "surname",
            "email",
        ]

        extra_kwargs = {
            "first_name": {"read_only": True},
            "email": {"read_only": True},
        }

    def to_representation(self, instance):
        return super().to_representation(instance)


##-- Update User Serializer-- ##


class UpdateUserSerializer(serializers.ModelSerializer):
    """Serializer to validate Update User"""

    class Meta:
        model = get_user_model()
        fields = ["id", "email", "first_name"]

        extra_kwargs = {
            "id": {"read_only": True},
            "email": {"read_only": True},
            "first_name": {"read_only": True},
        }


##-- Serializer For Basic Info --##
class BasicUserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = [
            "first_name",
            "surname",
        ]


##-- Serializer to register User--##
class RegisterUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    new_password_1 = serializers.CharField(write_only=True, required=True)
    new_password_2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "surname",
            "email",
            "new_password_1",
            "new_password_2",
        )
        extra_kwargs = {
            "id": {"read_only": True},
            "first_name": {"required": True},
            "surname": {"required": True},
            "email": {"required": True},
        }

    def validate(self, attrs: dict):
        ##-- Prevent email duplicacy and validate with password--##
        email = attrs.get("email")
        accepted_email = email.lower().strip()
        # cleaned_email = is_valid_email(accepted_email)
        if User.objects.filter(email__iexact=accepted_email).exists():
            raise serializers.ValidationError({"email": "Email already exist"})
        attrs["email"] = accepted_email

        if attrs["new_password_1"] != attrs["new_password_2"]:
            raise serializers.ValidationError({"password": "Incorrect password"})
        return super().validate(attrs)

    def create(self, validated_data: dict):
        """This method first creates the pending user, and then register the user after verification"""
        otp = generate_otp()
        email = validated_data.get("email")
        user, _ = PendingUser.objects.update_or_create(
            email=email,
            defaults={
                "email": email,
                "verification_code": otp,
                "password": make_password(validated_data.get("new_password_1")),
                "created_at": datetime.now(timezone.utc),
            },
        )
        user_info = {
            "otp": otp,
            "email": user.email,
        }
        send_account_verification_email.delay(user_info)
        return user
