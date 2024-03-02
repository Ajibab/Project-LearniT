from core.celery import app

from .util import send_account_verification_otp_to_email, send_password_reset_email_otp_to_email

@app.task()
def send_account_verification_email(user_info):
    send_account_verification_otp_to_email(user_info['email'], user_info['otp'], )
    

@app.task()
def send_password_reset_email(user_info):
    send_password_reset_email_otp_to_email(user_info['email'], user_info['otp'], )
    