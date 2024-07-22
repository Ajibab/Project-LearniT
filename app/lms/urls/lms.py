from django.urls import include, path
from rest_framework.routers import DefaultRouter

from ..views import ListCoursesViewsets,ModuleViewSet,ContentViewsets

app_name = "lms"

router = DefaultRouter()
router.register("courses", ListCoursesViewsets,basename="listofcourses")
router.register("module", ListCoursesViewsets, basename="listofmodules")
router.register("module", ModuleViewSet,basename="listoflessons")
router.register("contents",ContentViewsets,basename="contentoflesson")


urlpatterns = [
    path("", include(router.urls)),
]
