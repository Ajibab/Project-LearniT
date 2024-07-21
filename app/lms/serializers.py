import uuid
from .models import Course,UserCourseActivityTracker,Categories,Language,Module,ModuleTasksSubmission,Lesson,UserCertificate
from user.models import User
from rest_framework import exceptions, serializers
from django.db import models
from core.utilities.validators import is_admin,is_course_instructor,is_user_course_activity
from rest_framework.serializers import ModelSerializer


##-- Create the List Course Serializers --##
class ListCoursesSerializer(serializers.ModelSerializer):
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
        
class CourseUpgradeSerializer(serializers.ModelSerializer):
    """Allows Instructors and Admins to update courses"""
    class Meta:
        model = Course
        fields = '__all__'
        extra_kwags = {
            "instructor_profile":{"read_only":True}
        }
    def validate(self, attrs):
        user: User = self.context["request"].user
        if self.instance:
            if not is_admin(user) and user not in self.instance.instructor_profile.all():
                raise serializers.ValidationError({"course":"You cannot update this course because you are not an instructor"})
            return super().validate(attrs)
        
class UserCourseActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCourseActivityTracker
        fields = "__all__"

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = ['icon','name']
        extra_kwargs = {
            "icon": {"read_only": True}
        }
class DevelopModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model=Module
        fields = ['course','name']
        extra_kwags = {
            "name":{"read_only":True}
        }

    def validate(self, attrs):
        user: User = self.context["request"].user
        course:Course=self.instance.course if self.instance else attrs.get("course")
        if not is_admin(user) and not is_course_instructor(user,course):
            raise serializers.ValidationError(
                {'course':'You cannot create a module for a course you do not teach.'}
            )
        return super().validate(attrs)

class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ['course','name']
        extra_kwags = {
            "name":{"read_only":True}
        }

class ModuleTaskSubmissionSerializers(serializers.ModelSerializer):
    class Meta:
        model = ModuleTasksSubmission
        fields = ['module','user','assignment_upload']
        extra_kwags = {"assignment_upload":{"read_only":True}}

        def validate(self,attrs):
            user: User = self.context["request"].user
            if not is_admin(user) and user not in self.instance.is_user_course_activity():
                raise serializers.ValidationError({"course":"Only authenticated users can submit a task"})
            return super().validate(attrs)
        
class LessonsSerializer(serializers.ModelSerializer):
    """Allows Instructors and Admins to update lessons"""
    class Meta:
        model = Lesson
        fields = ['module','content','name']

        extra_kwargs = {
            'name': {'write_only': True},
            'content': {'write_only': True}
        }