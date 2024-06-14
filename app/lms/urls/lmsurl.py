from django.urls import include, path
from rest_framework.routers import DefaultRouter

from ..views import ListCoursesViewsets

app_name = "lms"

router = DefaultRouter()
router.register("", ListCoursesViewsets,basename="listofcourses")


urlpatterns = [
    path("listallcourses/",ListCoursesViewsets.as_view({'get': 'list'}), name="list-all-courses"),
    path("", include(router.urls)),
]
