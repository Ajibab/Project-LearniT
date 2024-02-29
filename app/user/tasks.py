from core.celery import app

from .util import send_otp_to_email

@app.task()
def send_email_notification(user_info):
    send_otp_to_email(user_info['message'], user_info['email'])
    