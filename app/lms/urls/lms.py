from django.urls import include, path
from rest_framework.routers import DefaultRouter

from ..views import ListCoursesViewsets,ModuleViewSet

app_name = "lms"

router = DefaultRouter()
router.register("courses", ListCoursesViewsets,basename="listofcourses")
router.register("modules", ListCoursesViewsets, basename="listofmodules")
router.register("lessons", ModuleViewSet,basename="listoflessons")


urlpatterns = [
    path("", include(router.urls)),
]
