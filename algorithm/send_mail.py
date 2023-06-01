import random
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.utils.html import strip_tags
from rest_framework.response import Response
from rest_framework import status

def mail_sending(email, payload, template, mail_subject):

    html_template = template

    print("html_template===============================================>", html_template)
    html_message = render_to_string(html_template, context=payload)
    subject = mail_subject
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    message = EmailMessage(subject, html_message, email_from, recipient_list)
    message.content_subtype = 'html'
    message.send()