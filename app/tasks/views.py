from django.shortcuts import render
from .serializers import QuizSerializer
from rest_framework import viewsets, filters,status
from .models import Quiz
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend

class QuizViewset(viewsets.ModelViewset):
    queryset = Quiz.objects.all().select_related("module")
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated,]
    #http_method_names = ["get",]


    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    search_fields = [
        "module",
        "task",
        "reattempt",
    ]
    ordering_fields = ["categories","title","description"]