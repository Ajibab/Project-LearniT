from django.shortcuts import render
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
from .models import Course, Categories
from .serializers import ListCoursesSerializer
from user.access import IsInstructor,IsLmsAdmin,IsLearner,IsPlatformAdmin


class ListCoursesViewsets(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = ListCoursesSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "patch", "delete"]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    search_fields = [
        "categories",
        "title",
        "description",
    ]
    ordering_fields = ["categories","title","description"]

    def list(self, request, *args, **kwargs):
        """Lists all courses on the LMS platform"""
        return super().list(request,*args,kwargs)

    def create(self,request,*args,**kwargs):
        """Create new course"""
        return super().create(request,*args,**kwargs)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    # For now, i think you should remove this get_queryset overriding
    # You override the get_queryset when you want to filter down data
    # based on the requirements. Regardless of authentication or not,
    # we want to show all courses to all users.
    def get_queryset(self):
        """gets courses by ID"""
        course: Course = self.request.course
        if course.IsAuthenticated:
            return super().get_queryset().all()
        return super().get_queryset().filter(id=course.id)
    

    def get_permissions(self):
        permission_class = self.permission_classes
        if self.action in ["list", "retrieve"]:
            permission_class = [AllowAny, IsLearner]
        elif self.action in["create","partial_update","update"]:
            permission_class = [IsInstructor,IsLmsAdmin,IsPlatformAdmin]
        elif self.action in ["destroy"]:
            permission_class = [IsLmsAdmin,IsPlatformAdmin]
        return [permission() for permission in permission_class]


