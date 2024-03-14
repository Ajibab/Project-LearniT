import pytest
from django.urls import reverse

from .conftest import api_client_with_credentials
from ..models import PendingUser 
pytestmark = pytest.mark.django_db

class TestUser:
    list_of_user_urls = reverse("user:user-list")

    def test_create_user(self,api_client,mocker):
        """This is the first test to a ascertain a valid user"""
        mock_send_otp = mocker.patch('user.tasks.send_account_verification_email.delay')

        data = {
            "email":"ajibolaolaosebikan@yahoo.com",
            "password":"password"}
            response = api_client.post(self.list_of_user_urls,data)
            assert response.status_code ==200

            pending_user = PendingUser.objects.get(email=data["email"])
            message_info = {
                'message': f"Account Verification!\nYour OTP for BotApp is {pending_user.verification_code}.\nIt expires in 10 minutes",
                'phone': data["phone"]
            }
            mock_send_otp.assert_called_once_with(message_info)    
        