# from django.shortcuts import render
import json
import time

import pandas as pd
import requests
from account.models import BrokerProfile, BrokersFileCSV, Profile
from account.serializers.broker import BrokerProfileSerializer
from algorithm.auto_password_generator import generate_password
from algorithm.send_mail import mail_sending
from algorithm.username_generator import auto_user
from authentication.models import User
from authentication.serializers.broker import (BrokerSerializer,
                                               UserSerializerWithToken)
from decouple import config
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
# from authentication.serializers import UserSerializerWithToken
from django.db import IntegrityError
from notifications.models import NotificationAction
from notifications.notification_temp import notification_tem
from rest_framework import parsers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

# ====================================Base =================================>

def create_broker_dataset(file_path):
    data = pd.read_csv(file_path, delimiter=',')
    list_of_csv = [list(row) for row in data.values]
    for l in list_of_csv:
        if type(l[0]) == float:
            continue
        qs = User.objects.all()
        email = l[22]
        email_list = []
        for user in qs:
            email_qs = user.email
            email_list.append(email_qs)
        if email in email_list:
            return False
        URL = l[0]
        ZPID = l[1]
        first_name = l[17]
        last_name = l[19]
        phone_number = l[20]
        zuid = l[21]
        address = l[23]
        profile_pic = l[24]
        print(l[23], l[24])
        password = generate_password()
        username = auto_user(email)
        if type(profile_pic) == float:
            profile_pic = None
        user = User.objects.create(
            first_name = first_name,
            last_name = last_name,
            username = username,
            email = email,
            password = make_password(password),
            type = "BROKER"
        )
        # Make Email from broker that new user
        payload = {}
        template = "wellcome.html"
        mail_subject = "Wellcome Immovision"
        print("email===============================>", email)
        mail_sending(email, payload, template, mail_subject)
        
        if user:
            profile = Profile.objects.get(user=user)
            profile.phone_number = phone_number
            profile.address = address
            profile.profile_pic = profile_pic
            profile.save()
        if profile:
            broker = BrokerProfile.objects.get(profile=profile)
            broker.zuid = zuid
            broker.save()
        time.sleep(1)




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


@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_broker(request):
    data = request.data
    user = request.user
    error = []
    if 'email' not in data:
        error.append({"error": "Please Enter Email of Broker"})
    if 'first_name' not in data:
        error.append({"error": "Please Enter First Name of Broker"})
    if 'last_name' not in data:
        error.append({"error": "Please Enter Last Name of Broker"})
    if 'phone_number' not in data:
        error.append({"error": "Please Enter Phone Number of Broker"})
    if 'zuid' not in data:
        error.append({"error": "Please Enter ZUID of Broker"})
    if 'address' not in data:
        error.append({"error": "Please Enter Address of Broker"})
    if 'language' not in data:
        error.append({"error": "Please Enter Language of Broker"})
    if len(error) > 0:
        print(error)
        return Response(error, status=status.HTTP_204_NO_CONTENT)
    if user.is_staff:
        first_name = data['first_name']
        last_name = data['last_name']
        broker_email = data['email']
        username = auto_user(broker_email)
        password = generate_password()
        
        try:
            user = User.objects.create(
                first_name = first_name,
                last_name = last_name,
                username = username,
                email = broker_email,
                password = make_password(password),
                type = "BROKER"
                )
            if user:
                profile = Profile.objects.get(user=user)
                profile.phone_number = data['phone_number']
                profile.address = data['address']
                profile.profile_pic = request.FILES.get('profile_image', profile.profile_pic)
                profile.save()
                NotificationAction.objects.create(
                    user=user
                )
            if profile:
                broker = BrokerProfile.objects.get(profile=profile)
                broker.zuid = data['zuid']
                broker.language = data['language']
                # broker.is_demo = True
                broker.save()
            print("---------------------------------> Password", password)
            ip_domain = config('DOMAIN')
            try:
                token_qs = RefreshToken.for_user(user)
                token = str(token_qs.access_token)
                print(token)
            except:
                token = ""
            one_time_link = f"{ip_domain}auth?token={token}"
            # ---------------------------------------This is Payload --------------------------
            print(one_time_link)
            # ----------------------------------------------------
            print("email===============================>", broker_email)
            payload = {
                    "one_time_link":one_time_link
                }
            template = "wellcome.html"
            mail_subject = "Wellcome to the emovision"
            # Please Make Template on Here Email For Broker
            title = "Create Account"
            desc = "Broker account successfully created"
            notification_type = "alert"
            LasUser = User.objects.all().last()
            #print("LasUser=======================================>", LasUser)
            notification_tem(user = LasUser, title = title, desc = desc, notification_type = notification_type)
            mail_sending(broker_email, payload, template, mail_subject)
            
            serializer = BrokerProfileSerializer(broker, many=False)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except IntegrityError as e:
            error_message = str(e)
            error = []
            if 'email' in error_message:
                error.append({"email":'user with this Email already exists'})
            if 'username' in error_message:
                error.append({'error':'user with this Username already exists'})
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
    return Response({"message": "You are not Authorize to make any Broker"}, status=status.HTTP_400_BAD_REQUEST)





@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_broker_csv(request):
    file = request.FILES.get('file')
    # if 'file' not in request.POST or file == None:
    #     return Response({"error": "Please Input Your File"}, status=status.HTTP_400_BAD_REQUEST)
    print(file)
    obj = BrokersFileCSV.objects.create(file=file)
    # print(obj)
    try:
        create = create_broker_dataset(obj.file)
        # if create:
        return Response({"message": "Upload CSV Broker Done"}, status=status.HTTP_200_OK)
        # else:
        #     return Response({"email":'user with this Email already exists'}, status=status.HTTP_400_BAD_REQUEST)
    except:
        return Response({"messsage": "Check your file please"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_broker(request, email):
    broker_qs = User.objects.filter(email=email)
    if not broker_qs.exists():
        return Response({'error': 'Broker Not Found'}, status=status.HTTP_400_BAD_REQUEST)
    broker_user = broker_qs.first()
    broker_user.delete()
    return Response({"message": "Delete Successfully"}, status=status.HTTP_200_OK)