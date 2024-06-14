import uuid
from .models import Course
from rest_framework import exceptions, serializers
from django.db import models
from rest_framework.serializers import ModelSerializer


##-- Create the List Course Serializers --##
class ListCoursesSerializer(ModelSerializer):
    """"This serializer lists/gets all the courses 
    (and their title, description and category) on the learning platform"""
    class Meta:
        model = Course
        fields = ['title', 
                  'description',
                  'category']
        extra_kwargs = {
            'title': {'write_only': True},
            'description': {'write_only': True}
        }
        
class GetACourseByIdSerializer(ModelSerializer):
    """ Given an ID, get a specific course"""

        