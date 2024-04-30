import pytest
from django.urls import reverse
from rest_framework import status

from .conftest import api_client_with_credentials

pytestmark = pytest.mark.django_db

class TestAuthenticationEndpoints:
    """"Testing the APIs"""
    login_url = reverse("authenticate:login")
    """With reverse(authenticate:login), an error was thrown(err:'authenticate' is not a registered namespace). 
    However, with reverse(login) the test was successful"""
    password_change_url = reverse("authenticate:password-change-list")
 
    def test_user_login(self, api_client, active_user, auth_user_password):
        data = {"email": active_user.email, "password":auth_user_password}
        response = api_client.post(self.login_url, data)
        assert response.status_code == status.HTTP_200_OK
        json_output = response.json()
        assert 'refresh' in json_output
        assert 'access' in json_output

    def test_declined_inactive_user_login(self, api_client, inactive_user, auth_user_password):
        """Inactive users are denied login"""
        data = {"email":inactive_user.email, "password":auth_user_password}
        response = api_client.post(self.login_url,data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_deny_login_invalid_credentials(self, api_client, active_user):
        """Test case to reject users with invalid inforation"""
        data = {"email": active_user.email, "password": "na@youtrypass"}
        response = api_client.post(self.login_url, data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_password_change_with_valid_old_password(self,api_client,auth_user_password,authenticate_user):
        """Check that users can change password successfully with valid old password"""
        user = authenticate_user()
        token = user["token"]
        user_instance = user["user_instance"]
        data = {"old_password":auth_user_password,
                "new_password_1": "ajibolaaa@@",
                }
        api_client_with_credentials(token, api_client)
        response = api_client.post(self.password_change_url,data,format="json")
        print(response.json())
        assert response.status_code == status.HTTP_200_OK
        user_instance.refresh_from_db()
        assert user_instance.check_password("ajibolaaa@@")