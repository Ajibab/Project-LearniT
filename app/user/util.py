import base64
import os
import re
import pyotp
from django.conf import settings
from django.core.mail import send_mail
from rest_framework import serializers

"""I am unable to set-up an email service using 
SendGrid and Twilio. The platform seems t require
extra security check"""


def is_valid_email(email):
    ##--The regular expression pattern for email validation--##
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    ##--match the email pattern with regular expression--##
    match = re.match(pattern, email)
    if match:
        return True
    else:
        raise serializers.ValidationError({"phone": "Incorrect phone number."})


def generate_otp() -> int:
    totp = pyotp.TOTP(base64.b32encode(os.urandom(16)).decode("utf-8"))
    otp = totp.now()
    return otp


def send_account_verification_otp_to_email(email, otp):
    """The OTP is send the email address"""
    subject = "Your VERIFICATION OTP"
    message = f"Hi there.\nUse this OTP to verify your account: {otp}"
    from_email = settings.EMAIL_HOST_USER
    email_recipient = [email]
    send_mail(subject, message, from_email, email_recipient)


def send_password_reset_email_otp_to_email(email, otp):
    """The OTP is sent to the email address for password reset"""
    subject = "Your PASSWORD RESET OTP"
    message = f"Hi there.\nUse this OTP to reset your password: {otp}"
    from_email = settings.EMAIL_HOST_USER
    email_recipient = [email]
    send_mail(subject, message, from_email, email_recipient)

#TODOs: check how to use template for sending email