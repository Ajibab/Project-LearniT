from django.contrib.auth import get_user_model
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.settings import api_settings
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import filters, status, viewsets, serializers
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import User, Token

from .enums import TokenEnum
from .serializers import (
    RegisterUserSerializer,
    ObtainTokenSerializer,
    ChangePasswordSerializer,
    UpdateUserSerializer,
    AuthTokenSerializer,
    CreatePasswordFromChangedOTPSerializer,
    EmailSerializer,
    InitiatePasswordResetSerializer,
    ListUserSerializer,
    AccountVerificationSerializer,
)


class CustomObtainTokenPairViewSets(TokenObtainPairView):
    """Use email and password to authenticate"""

    class_serializer = ObtainTokenSerializer


class AuthenticationViewSet(viewsets.GenericViewSet):
    """Authenticate users viewsets"""

    serializer_class = EmailSerializer
    permission_classes = [IsAuthenticated]

    """The get_permission function will grant access to users who have
    a verified account"""

    def get_permissions(self):
        permsission_classes = self.permission_classes
        if self.action in [
            "initiate_password_reset",
            "create_password",
            "verify_account",
        ]:
            permsission_classes = [AllowAny]
        return [permission() for permission in permsission_classes]

    @action(
        methods=["POST"],
        detail=False,
        serializer_class=InitiatePasswordResetSerializer,
        url_path="initiate-password-reset",
    )
    def initiate_password_reset(self, request, pk=None):
        """Send an OTP to user's email for password reset"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"success": True, "message": "Temporay password sent to your email!"}
        )

    @action(
        methods=["POST"],
        detail=False,
        serializer_class=CreatePasswordFromChangedOTPSerializer,
    )
    def create_password(self, request, pk=None):
        """This method enables users to create a new password having received the OTP sent to the User's Email"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token: Token = Token.objects.filter(
            token=request.data["otp"], token_type=TokenEnum.PASSWORD_RESET
        ).first()
        if not token or not token.is_valid():
            return Response(
                {"success": False, "errors": "Invalid password reset otp"}, status=400
            )
        token.reset_user_password(request.data["new_password"])
        token.delete()
        return Response(
            {"success": True, "message": "Password reset successful"},
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        responses={
            200: inline_serializer(
                name="AccountVerificationStatus",
                fields={
                    "success": serializers.BooleanField(default=True),
                    "message": serializers.CharField(
                        default="Successful Verified Account"
                    ),
                },
            )
        }
    )
    @action(
        methods=["POST"],
        detail=False,
        serializer_class=AccountVerificationSerializer,
        url_path="verify-account",
    )
    def verify_account(self, request, pk=None):
        """This method activates the user account using the OTP sent the user's email"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"success": True, "message": "Account Verification Successful"}, status=200
        )


class ChangePasswordViewSets(viewsets.GenericViewSet):
    """Allow authenticated users to reset password"""

    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "Your password has been updated"}, status.HTTP_200_OK
        )


class CreateTokenView(ObtainAuthToken):
    """A new authentication token is created for user"""

    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        try:
            token, created = Token.objects.get_or_create(user=user)
            return Response(
                {"token": token.key, "created": created, "roles": user.roles},
                status=status.HTTP_200_OK,
            )
        except Exception as error:
            return Response({"message": str(error)}, 500)


class RegisterUserViewsets(viewsets.ModelViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = ListUserSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "patch", "delete"]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    search_fields = [
        "email",
        "first_name",
        "surname",
        "phone_number",
    ]

    ordering_fields = ["email", "first_name", "surname", "phone_number"]

    def get_queryset(self):
        user: User = self.request.user
        if user.is_admin:
            return super().get_queryset().all()
        return super().get_queryset().filter(id=user.id)

    ##-- Onboard User if account is created--##
    def get_serializer_class(self):
        if self.action == "create":
            return RegisterUserSerializer
        if self.action in ["partial_update", "update"]:
            return UpdateUserSerializer
        return super().get_serializer_class()

    ##-- Set Permission Requests --##
    def get_permissions(self):
        permission_class = self.permission_classes
        if self.action in ["create"]:
            permission_class = [AllowAny]
        elif self.action in ["list", "retrieve", "partial_update", "update"]:
            permission_class = [IsAuthenticated]
        elif self.action in ["destroy"]:
            permission_class = [IsAuthenticated]
        return [permission() for permission in permission_class]

    @extend_schema(
        responses={
            200: inline_serializer(
                name="VerificationStatus",
                fields={
                    "success": serializers.BooleanField(default=True),
                    "message": serializers.CharField(
                        default="OTP sent for verification"
                    ),
                },
            ),
        },
        description="Sign up with a verified email address.",
    )
    def create(self, request, *args, **kwargs):
        """Account creation for the user"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"success": True, "message": "OTP sent to your email for verification!"},
            status=200,
        )

    ##-- Enable Admin To Retrieve the Sytem's List of User--##
    def retrieve(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
