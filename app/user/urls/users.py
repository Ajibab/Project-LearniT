from django.urls import include, path
from rest_framework.routers import DefaultRouter

from ..views import RegisterUserViewsets

app_name = "users"

router = DefaultRouter()
router.register("", RegisterUserViewsets)


urlpatterns = [
    path("", include(router.urls)),
]