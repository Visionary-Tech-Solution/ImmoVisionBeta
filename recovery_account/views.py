import random

from account.models import User
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from rest_framework import generics, response, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .serializer import EmailSerializer, ResetPasswordSerializer


class PasswordReset(generics.GenericAPIView):
    serializer_class = EmailSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data["email"]

        user_qs = User.objects.filter(email=email)
        user = user_qs.first()
 
        if user:
            def generate_unique_token():
                while True:
                    password_reset_token = random.randint(1, 9999999999999999999)
                    try:
                        User.objects.get(password_reset_token=password_reset_token)
                    except User.DoesNotExist:
                        return password_reset_token
                    
            password_reset_token = generate_unique_token()
            user.password_reset_token = password_reset_token

            
            def generate_unique_otp():
                while True:
                    password_reset_OTP = random.randint(1, 99999)
                    try:
                        User.objects.get(password_reset_OTP=password_reset_OTP)
                    except User.DoesNotExist:
                        return password_reset_OTP
                    
            
            password_reset_OTP = generate_unique_otp()
            user.password_reset_OTP = password_reset_OTP

            
            mydict = {
                'password_reset_token':password_reset_OTP
            }

            html_template = 'reset_password.html'
            html_message = render_to_string(html_template, context=mydict)

            subject = 'Your forget password token'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [user.email]
            message = EmailMessage(subject, html_message, email_from, recipient_list)
            message.content_subtype = 'html'
            user.save()
            #message.send()

            return response.Response(
                {
                    "message": "Please check your mail an OTP is sent.",
                    "recovery_token": str(password_reset_token)
                },
                status=status.HTTP_200_OK,
            )
        else:
            return response.Response(
                {"message": "User doesn't exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        

class ResetPasswordSendTokenApi(generics.GenericAPIView):

    serializer_class = ResetPasswordSerializer
    def post(self, request, *args, **kwargs):
        
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        password_reset_token = request.data["password_reset_token"]
        password_reset_OTP = request.data["password_reset_OTP"]
        new_password = serializer.data["new_password"]

        user = User.objects.filter(password_reset_OTP=password_reset_OTP,password_reset_token=password_reset_token).first()
        print("Recovery User=========================================", user)
        if user:
            user.set_password(new_password)
            user.password_reset_token = ""
            user.password_reset_OTP = ""
            user.save()

            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "message": "Successfully password changed",
                    'access_token': str(refresh.access_token),
                },status=status.HTTP_202_ACCEPTED
            )
        else:
            return Response(
                {
                    "message": "Invalid token or OTP"
                },status=status.HTTP_400_BAD_REQUEST
            )
    


