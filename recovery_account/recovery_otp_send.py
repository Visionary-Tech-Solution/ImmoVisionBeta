from django.core.mail import send_mail
import random
from django.conf import settings
from account.models import (
    User
)
from django.template.loader import render_to_string
from django.core.mail import EmailMessage

def send_otp_via_email(email):
    user_obj = User.objects.get(email=email)
    
    try:
        password_reset_token = random.randint(1,999999)
        user_obj.password_reset_token = password_reset_token

    except:
        password_reset_token = random.randint(1,999999)
        user_obj.password_reset_token = password_reset_token

    user_obj.save()

    mydict = {
        'otp':f"{password_reset_token}"
    }
    html_template = 'verified_emaii_otp.html'
    html_message = render_to_string(html_template, context=mydict)
    subject = 'Password Reset Token'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    message = EmailMessage(subject, html_message, email_from, recipient_list)
    message.content_subtype = 'html'
    #message.send()

    