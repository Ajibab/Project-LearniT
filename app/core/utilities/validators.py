from typing import List
from user.models import User
from lms.models import Course,Module
from rest_framework import serializers

def is_admin(user:User) ->bool:
    """Verifies if a user is LmsAdmin or PlatformAdmin"""
    user_roles: List[str] = user.roles
    if "LMS_ADMIN" in user_roles:
        return True
    if "PLATFORM_ADMIN" in user_roles:
        return True
    return False

def is_course_instructor(user:User,course:Course)->bool:
    """Verifies if user is a course instructor on the LMS platform"""
    course_instructor:User = course.instructor_profile.all()
    if user in course_instructor:
        return True
    return False

def is_user_course_activity(user:User, module:Module)->bool:
    """checks if a learner is active on the course"""
    active_learner = module.course.user_activity_count.all()
    if not active_learner.filter(user=user).exists():
        raise serializers.ValidationError({"module": "You have no activities for this course"})
    return True
