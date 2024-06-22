from rest_framework import permissions

class IsLmsAdmin(permissions.BasePermission):
    """Allows access to only the admins of the
    Learning Management System."""
    message = "Only the LMS Admins are authorized to perform this action"

    def has_permission(self, request, view):
        return bool(
            request.user.is_authenticated and "LMS_ADMIN" in request.user.roles
        )

class IsLearner(permissions.BasePermission):
    """Allows access only to authenticated learners."""
    message = "Only Learners are authorized to perform this action."

    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and "LEARNER" in request.user.roles)
    

class IsInstructor(permissions.BasePermission):
    """Allows access only to instructors"""
    message = "Only instructors are authorized to perform this action."

    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and "TEACHER" in request.user.roles)
    
class IsPlatformAdmin(permissions.BasePermission):
    """Allows access only to instructors"""
    message = "Only teachers are authorized to perform this action."

    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and "PLATFORM_ADMIN" in request.user.roles)
