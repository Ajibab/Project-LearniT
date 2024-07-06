from typing import List
from django.shortcuts import render
from django.db.models import Exists, Q
from django.contrib.auth import get_user_model
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.settings import api_settings
from rest_framework import viewsets, filters, status
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import filters, status, viewsets, serializers
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import Course, Categories, Module
from .serializers import (ListCoursesSerializer,ModuleSerializer,
                          CourseUpgradeSerializer,DevelopModuleSerializer)
from user.access import IsInstructor,IsLmsAdmin,IsLearner,IsPlatformAdmin


class ListCoursesViewsets(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = ListCoursesSerializer
    permission_classes = [IsAuthenticated,]
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

    # Work to be completed
    """
    3 List all modules in a course    --courses/{course_id}/modules
    4 Given a module, return its lessons --- modules/{module_id}/lessons
    5 Given a lesson, return its content --- lessons/{lesson_id}

    How to ?

    3. add a new api using custom action in drf to list all modules in a course.
    the endpoint would neeed to be part of this class

    4. Create a new class called ModuleViewSet, 
        create a new detail endpoint using action as done above to retrieve all lessons in a module
        remember to link a url with it. Repeat this same process for number 5. which is lesson.
    """
    def get_permissions(self):
        permission_classes = self.permission_classes
        if self.action in ["list", "retrieve"]:
            permission_classes = [IsLearner]
        elif self.action in["create","partial_update","update"]:
            permission_classes = [IsInstructor | IsLmsAdmin | IsPlatformAdmin]
        elif self.action in ["destroy"]:
            permission_classes = [IsLmsAdmin | IsPlatformAdmin]
        return [permission() for permission in permission_classes]
    
    """ Create a custom action API to retrieve a module given a course"""
    @action(
        detail=True,
        methods= ["GET"],
        permission_classes=[AllowAny],
        serializer_class=ModuleSerializer,
        url_path= "modules",
    )
    def get_module_given_a_course(self,request,*args,**kwargs):
        """This will return all modules given a course"""
        user=self.request.user
        course_instance: Course=self.get_object()
        modules: List [Module] = course_instance.modules
        ## after getting the module, pass it through serializer
        active_learner = course_instance.user_activity_count.all()
        is_active_learner = active_learner.filter(user=user).exists()
        serializer_class_ = ModuleSerializer if IsLmsAdmin(
            user) or is_active_learner or user in course_instance.instructor_profile.all() else None
        data = serializer_class_(
            instance=modules, context={"request": request}, many=True
        ).data

        return Response( {"success": True, "data": data}, status.HTTP_200_OK)



