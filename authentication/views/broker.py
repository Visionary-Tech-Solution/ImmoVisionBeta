# from django.shortcuts import render
import json

import requests
# from authentication.serializers import UserSerializerWithToken
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework import parsers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from algorithm.send_mail import mail_sending
from authentication.models import User
from authentication.serializers.broker import (BrokerSerializer,
                                               UserSerializerWithToken)

# class BrokerView(APIView):
#     parser_classes = (parsers.FormParser, parsers.MultiPartParser)
#     def post(self, request):
#         data = request.data
#         email = data.get("email")
#         template = "welcome_email.html"
#         payload = {}
#         mail_subject = f"Wellcome to immovision"

#         serializer = BrokerSerializer(data=data)
#         if serializer.is_valid():
#             serializer.save()

#             print("Broker mail===========================================>", data.get("email"))
#             print("Template============================>", template)

#             mail_sending(email, payload, template, mail_subject)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class GoogleLoginCallback(APIView):
    def post(self, request):
        data = request.data
        serializer = UserSerializerWithToken(data=data)

        if serializer.is_valid():

            access_token = request.data.get('access_token')

            print("ACCESSTOKEN==============================>", access_token)

            if not access_token:
                return Response('Access token missing', status=status.HTTP_400_BAD_REQUEST)
                
            user_info = self.fetch_user_info(access_token)

            email = user_info.get('email')

            if user_info:
                email = user_info.get('email')
                try:
                    user = User.objects.get(email=email)
                    #user = authenticate(request, username=user.username, password="")
                    
                    if user is not None:
                        #login(request, user)
                        refresh = RefreshToken.for_user(user)
                        access_token = str(refresh.access_token)
                        response_data = {
                            'access_token': access_token,
                            'user': {
                                'id': user.id,
                                'username': user.username,
                                'email': user.email,
                                'first_name': user.first_name,
                                'last_name': user.last_name,
                            },
                            'type': "BROKER",
                        } 

                        return Response(response_data, status=status.HTTP_200_OK)
                    else:
                        return Response({"Cool faild"}, status=status.HTTP_200_OK)
                        
                    
                except User.DoesNotExist:
                    user = User.objects.create(email=email, username=email, type="BROKER")
                    user.first_name = user_info.get('given_name')
                    user.last_name = user_info.get('family_name')
                    #user.set_password('')
                    user.save()
                    #user = authenticate(username=user.username, password='')

                    if user is not None:
                        #login(request, user)
                        refresh = RefreshToken.for_user(user)
                        access_token = str(refresh.access_token)
                        response_data = {
                            'access_token': access_token,
                            'user': {
                                'id': user.id,
                                'username': user.username,
                                'email': user.email,
                                'first_name': user.first_name,
                                'last_name': user.last_name,

                            },
                            'type': "BROKER",
                        }

                        return Response(response_data, status=status.HTTP_200_OK)
                    else:
                        
                        return Response('Authentication failed', status=status.HTTP_400_BAD_REQUEST)

            else:
                return Response('Failed to fetch user information', status=status.HTTP_400_BAD_REQUEST)


    def fetch_user_info(self, access_token):
        try:
            headers = {'Authorization': f'Bearer {access_token}'}
            response = requests.get('https://www.googleapis.com/oauth2/v3/userinfo', headers=headers)

            if response.ok:
                user_info = json.loads(response.content)
                return user_info
            else:
                return None
        except requests.exceptions.RequestException as e:
            print(e)
            return None 

