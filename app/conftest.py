import pytest
from django.urls import reverse
from ..models import User
from pytest_factoryboy import register
from rest_framework.test import APIClient 
from .factories import UserFactory,TokenFactory

"This conftest is a centralized point for all fixtures"
register(UserFactory)
register(TokenFactory)

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def active_user(db, user_factory):
    return user_factory.create(is_active=True)

@pytest.fixture
def auth_user_password() -> str:
    return password

@pytest.fixture
def inactive_user(db, user_factory):
    user = user_factory.create(is_active=False)
    return user

@pytest.fixture
def authenticate_user(api_client,active_user:User,auth_user_password):
    def _user(verified=True, is_active=True,is_admin=False):
        active_user.verified = verified
        active_user.is_active = is_active
        active_user.is_admin = is_admin
        active_user.save()
        active_user.refresh_from_db()
        url = reverse("auth:login")
        data = {
            "phone": active_user.email,
            "password": auth_user_password,
        }
        response = api_client.post(url,data)
        token = response.json()["access"]
        return{
            "token": token,
            "user_email": active_user.email,
            "user_instance": active_user,
        }
    return _user