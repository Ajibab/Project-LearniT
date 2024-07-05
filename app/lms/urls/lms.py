from django.urls import include, path
from rest_framework.routers import DefaultRouter

from ..views import ListCoursesViewsets

app_name = "lms"

router = DefaultRouter()
router.register("courses", ListCoursesViewsets,basename="listofcourses")
router.register("modules", ListCoursesViewsets, basename="listofmodules")


urlpatterns = [
    path("", include(router.urls)),
]
