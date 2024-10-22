from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import(TokenRefreshView,TokenVerifyView)
from ..views import (
    CustomObtainTokenPairViewSets,
    ChangePasswordViewSets,AuthenticationViewSet
)
app_name = "authenticate"
router = DefaultRouter()
router.register("",AuthenticationViewSet,basename="authenticate")
router.register("change-password",ChangePasswordViewSets,basename="password-change")

urlpatterns = [
    path("login/",CustomObtainTokenPairViewSets.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="refresh-token"),
    path("token/verify", TokenVerifyView.as_view(), name="verify-token"),
    path("",include(router.urls)),
]