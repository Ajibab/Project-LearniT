from django.shortcuts import render
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import filters,status,viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import User, PendingUser

from .serializers import (
    RegisterUserSerializer,
    ObtainTokenSerializer,
    ChangePasswordSerializer, UpdateUserSerializer,
)
class CustomObtainTokenPairViewSets(TokenObtainPairView):
    """Use email and password to authenticate"""
    class_serializer = ObtainTokenSerializer

class ChangePasswordViewSets(viewsets.GenericViewSet):
    """Allow authenticated users to reset password"""
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({"message":"Your password has been updated"}, status.HTTP_200_OK)
    
class RegisterUserViewsets(viewsets.ModelViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = RegisterUserSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = [
        "get",
        "post",
        "patch",
        "delete"
    ]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    search_fields = [
        "email",
        "first_name",
    ]
    
    ordering_fields = [
        "email",
        "first_name",
    ]

    def get_queryset(self):
        user: User = self.request.user
        if user.is_admin:
            return super().get_queryset().all()
        return super().get_queryset().filter(id=user.id)
    
    ##-- Onboard User if account is created--##
    def get_serializer_class(self):
        if self.action == "create":
            return RegisterUserSerializer
        if self.action in ["partial_update"]:
            return UpdateUserSerializer
        return super().get_serializer_class()
    
    ##-- Set Permission Requests --##
    def get_permissions(self):
        permission_class = self.permission_classes
        if self.action in ["create"]:
            permission_class = [AllowAny]
        elif self.action in ["list", "retrieve","partial_update","update"]:
            permission_class = [IsAuthenticated]
        return [permission_class() for permission in permission_class]
    
    ##-- Automatically Activate Account Upon Creation--##
    @extend_schema(responses={200: RegisterUserSerializer()})
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"success": True, "message": "Account Created Successfully"}, status=200)
    
    

    ##-- Enable Admin To Retrieve the Sytem's List of User--##
    def retrieve(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)