import base64
import os
import re
import pyotp
from django.conf import settings
from rest_framework import permissions,serializers
from twilio.rest import Client
from .models import User
from .enums import SytemRoleEnum

"""I am unable to set-up an email service using 
SendGrid and Twilio. The platform seems t require
extra security check"""

#client = Client(settings.TWILIO_ACCOUNT_SID,settings.TWILIO_AUTH_TOKEN)

def send_message(message:str,email:str):
    Client.messages.create(
        body=message,
        from_=settings.TWILIO_PHONE_NUMBER,
        to=email
    )

    return

def is_valid_email(email):
    ##--The regular expression pattern for email validation--##
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    ##--match the email pattern with regular expression--##
    match = re.match(pattern,email)
    if match:
        return True
    else:
        raise serializers.ValidationError({'phone': 'Incorrect phone number.'})
    
def generate_otp()->int:
    totp = pyotp.TOTP(base64.b32encode(os.urandom(16)).decode('utf-8'))
    otp = totp.now()
    return otp