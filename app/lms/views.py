from typing import List
from rest_framework.decorators import action
from rest_framework import viewsets, filters, status
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import filters, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .models import Course, Module, Lesson
from .serializers import (ListCoursesSerializer,ModuleSerializer,LessonsSerializer)
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
    def get_modules_given_a_course(self,request,*args,**kwargs):
        """This will return all modules given a course"""
        course_instance: Course=self.get_object()
        modules: List [Module] = course_instance.total_modules
        serializer_class_ = ModuleSerializer
        data = serializer_class_(
            instance=modules, context={"request": request}, many=True
        ).data

        return Response( {"success": True, "data": data}, status.HTTP_200_OK)
    
class ModuleViewSet(viewsets.ModelViewSet):
    """This viewset entails the endpoints needed to retrieve a lesson given a module."""
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    permission_classes = [IsAuthenticated,]
    http_method_names = ["get",]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    search_fields = [
        "name",
        "module",
    ]
    ordering_fields = ["names","modules",]


    @extend_schema(exclude=True)
    def list(self, request, *args, **kwargs):
        """Lists all lessons on the LMS platform"""
        return super().list(request,*args,kwargs)

    def create(self,request,*args,**kwargs):
        """Create new lessons"""
        return super().create(request,*args,**kwargs)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def get_permissions(self):
        permission_classes = self.permission_classes
        if self.action in ["list", "retrieve"]:
            permission_classes = [IsLearner]
        elif self.action in["create","partial_update","update"]:
            permission_classes = [IsInstructor | IsLmsAdmin | IsPlatformAdmin]
        elif self.action in ["destroy"]:
            permission_classes = [IsLmsAdmin | IsPlatformAdmin]
        return [permission() for permission in permission_classes]
    
    """ Create a custom action API to retrieve Lessons given a Module"""
    @action(
        detail=True,
        methods= ["GET"],
        permission_classes=[AllowAny],
        serializer_class=LessonsSerializer,
        url_path= "lessons",
    )
    def get_lessons_given_a_module(self,request,*args,**kwargs):
        """This will return all Lessons given a Module"""
        module_instance: Module=self.get_object()
        lessons: List [Lesson] = module_instance.total_lessons
        serializer_class_ = LessonsSerializer
        data = serializer_class_(
            instance=lessons, context={"request": request}, many=True
        ).data

        return Response( {"success": True, "data": data}, status.HTTP_200_OK)
    
class ContentViewsets(viewsets.ModelViewSet):
    """This endpoint retrieves content given a lesson"""
    queryset = Lesson.objects.all()
    serializer_class = LessonsSerializer
    permission_classes = [IsAuthenticated,]
    http_method_names = ["get"]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    search_fields = [
        "name",
        "module",
        "content",
        "module__name",
    ]
    ordering_fields = ["name","module","content",]

    def get_permissions(self):
        permission_classes = self.permission_classes
        if self.action in ["retrieve"]:
            permission_classes = [IsLearner]
        elif self.action in["create","partial_update","update"]:
            permission_classes = [IsInstructor | IsLmsAdmin | IsPlatformAdmin]
        elif self.action in ["destroy"]:
            permission_classes = [IsLmsAdmin | IsPlatformAdmin]
        return [permission() for permission in permission_classes]
    
    """ Create a custom action API to retrieve Contents given a Lesson"""
    @action(
        detail=True,
        methods= ["GET"],
        permission_classes=[AllowAny],
        serializer_class=LessonsSerializer,
        url_path= "contents",
    )
    def get_contents_given_a_lesson(self,request,*args,**kwargs):
        """This will return all Contents given a Lesson"""
        lesson_instance: Lesson=self.get_object()
        serializer_class_ = LessonsSerializer
        data = serializer_class_(
            instance=lesson_instance, context={"request": request},
        ).data

        return Response( {"success": True, "data": data}, status.HTTP_200_OK)
    
    

