# from django.shortcuts import render
from account.models import Profile
from algorithm.auto_password_generator import generate_password
from algorithm.send_mail import mail_sending
from algorithm.username_generator import auto_user
from authentication.models import User
from authentication.serializers.base_auth import UserCreationSerializer
from authentication.serializers.broker import BrokerSerializer
from decouple import config
# from authentication.serializers import UserSerializerWithToken
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.db import IntegrityError
from notifications.models import NotificationAction
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response


@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_freelancer(request):
    data = request.data
    user = request.user
    if 'email' not in data:
        print("Error Email")
        return Response({"message": "Please Enter Email of Freelancer"}, status=status.HTTP_204_NO_CONTENT)
    if user.is_staff:
        freelancer_email = data['email']
        username = auto_user(freelancer_email)
        password = generate_password()
        
        try:
            user = User.objects.create(
                email = freelancer_email,
                username = username,
                password = make_password(password),
                type = "FREELANCER"
                )
            print("---------------------------------> Password", password)
            ip_domain = config('DOMAIN')
            NotificationAction.objects.create(
                user = user
            )
            if user:
                template = "freelancer_template.html"
                mail_subject = "Congragulation for be a Immovation freelancer"
                payload = {
                    "email":freelancer_email,
                    "password":password,
                    "login_link":f"{ip_domain}"
                }
                mail_sending(freelancer_email, payload, template, mail_subject)
            
            serializer = UserCreationSerializer(user, many=False)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except IntegrityError as e:
            error_message = str(e)
            error = []
            if 'email' in error_message:
                error.append({"email":'user with this Email already exists'})
            if 'username' in error_message:
                error.append({'error':'user with this Username already exists'})
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
    return Response({"message": "You are not Authorize to make any Freelancer"}, status=status.HTTP_400_BAD_REQUEST)



