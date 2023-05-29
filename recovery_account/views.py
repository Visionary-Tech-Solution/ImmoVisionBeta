from rest_framework import (
    generics,
    status,
    response
)
from django.conf import settings
from account.models import (
    User
)
from .serializer import(
    EmailSerializer,
    ResetPasswordSerializer
)
from django.conf import settings 
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from rest_framework.response import Response
from rest_framework import status
import random
from rest_framework_simplejwt.tokens import RefreshToken


class PasswordReset(generics.GenericAPIView):
    serializer_class = EmailSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data["email"]

        print("PasswordEmail===============================================", email)


        user = User.objects.filter(email=email).first()
 
        if user:
            password_reset_token = random.randint(1,99999934535464646)
            
            mydict = {
                'password_reset_token':password_reset_token
            }

            html_template = 'email.html'
            html_message = render_to_string(html_template, context=mydict)

            subject = 'Your forget password token'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [user.email]
            message = EmailMessage(subject, html_message, email_from, recipient_list)
            message.content_subtype = 'html'
            user.password_reset_token = password_reset_token
            user.save()
            message.send()

            return response.Response(
                {
                    "message": "Please check your mail a token is sent."

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
        password_reset_token = serializer.data["password_reset_token"]
        new_password = serializer.data["new_password"]

        user = User.objects.filter(password_reset_token=password_reset_token).first()
        if user:
            user.set_password(new_password)
            user.password_reset_token = ""
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
                    "message": "Invalid token"
                },status=status.HTTP_400_BAD_REQUEST
            )
    


