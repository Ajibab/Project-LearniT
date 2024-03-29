import pytest
from django.urls import reverse
from mock import patch
from unittest.mock import Mock


from .conftest import api_client_with_credentials
from ..models import PendingUser 
pytestmark = pytest.mark.django_db

class TestUser:
    list_of_user_urls = reverse("users:user-list")
    

    def test_create_user(self,api_client,mocker):
        """This is the first test to a ascertain a valid user"""
        mock_send_otp = mocker.patch('user.tasks.send_account_verification_email.delay')

        data = {
            "email":"ajibolaolaosebikan@yahoo.com",
            "first_name": "Ajibola",
            "surname": "Olaosebikan",
            "new_password_1":"password@1",
            "new_password_2":"password@1"}
        response = api_client.post(self.list_of_user_urls,data)
        #print(response.json())
        assert response.status_code == 200

        pending_user = PendingUser.objects.get(email=data["email"])
        message_info = {
                'message': f"Account Verification!\nYour OTP for BotApp is {pending_user.verification_code}.\nIt expires in 10 minutes",
                'email': data["email"]
            }
        #mock_send_otp.assert_called_once_with(message_info)   

    def test_unable_to_create_user_with_invalid_email(self, api_client,mocker):
        """This test is to ensure a user with invalid information cannot register"""
        data = {
            "email": "ajibolaolaosebikan.com",
            "first_name": "Ajibola",
            "surname": "Olaosebikan",
            "new_password_1":"password@1",
            "new_password_2":"password@1"
        }
        response = api_client.post(self.list_of_user_urls,data)
        assert response.status_code== 400
        