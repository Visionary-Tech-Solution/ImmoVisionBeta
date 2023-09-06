# from django.shortcuts import render
import json
import time

import pandas as pd
import requests
from decouple import config
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
# from authentication.serializers import UserSerializerWithToken
from django.db import IntegrityError
from rest_framework import parsers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from account.models import BrokerProfile, BrokersFileCSV, Profile
from account.serializers.broker import BrokerProfileSerializer
from algorithm.auto_password_generator import generate_password
from algorithm.send_mail import mail_sending
from algorithm.username_generator import auto_user
from authentication.models import User
from authentication.serializers.broker import (BrokerSerializer,
                                               UserSerializerWithToken)
from notifications.models import NotificationAction
from notifications.notification_temp import notification_tem

# ====================================Base =================================>

def create_broker_dataset(file_path):
    data = pd.read_csv(file_path, delimiter=',')
    list_of_csv = [list(row) for row in data.values]
    for l in list_of_csv:
        print(l)
        if type(l[6]) == float:
            continue
        qs = User.objects.all()
        email = l[6] # 22
        
        email_list = []
        for user in qs:
            email_qs = user.email
            email_list.append(email_qs)

        
        if email in email_list:
            continue
            # return False
        if  type(l[5]) == float:
            URL = None
        else:
            URL = l[5]

        #ZPID = l[8]
        if type(l[1]) == float:
            first_name=None
        else:
            first_name = l[1]
        if type(l[2]) == float:
            last_name=None
        else:
            last_name = l[2]

        if type(l[4]) == float:
            profile_pic = None
        else:
            profile_pic = l[4]

        password = '123456'#generate_password()
        username = auto_user(email)

        print(first_name)
        print(last_name)
        print(email)

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
        # try:
        #     mail_sending(email, payload, template, mail_subject)
        # except Exception as e:
        #     print(e, "Error on Create Broker.")
        
        if user:
            profile = Profile.objects.get(user=user)
            if type(l[8]) != float:
                profile.phone_number = l[8]
            # profile.address = address
            profile.profile_pic = profile_pic
            profile.save()
        if profile:
            broker = BrokerProfile.objects.get(profile=profile)
            #broker.zuid = zuid
            broker.realtor_profile_url = URL
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
    else:
        zuid = data['zuid']
    if 'realtor_profile_url' in data:
        realtor_profile_url = data['realtor_profile_url']
    else:
        realtor_profile_url = None
    if 'address' not in data:
        error.append({"error": "Please Enter Address of Broker"})
    if 'language' not in data:
        error.append({"error": "Please Enter Language of Broker"})
    if len(error) > 0:
        print(error)
        return Response(error, status=status.HTTP_204_NO_CONTENT)
    
    if len(zuid) == 0 or zuid == "None":
        zuid = None
    
    if realtor_profile_url is not None:
        if len(realtor_profile_url) == 0 or realtor_profile_url == "None":
            realtor_profile_url = None

    profile_image = request.FILES.get('profile_image')
    
    if user.is_staff:
        first_name = data['first_name']
        last_name = data['last_name']
        broker_email = data['email']
        username = auto_user(broker_email)
        password = "123456"
        
        # print(profile_image, "--------------------Profile Image")
        # print(data['profile_image'])
        # print(input("--------------------->"))

        try:
            user = User.objects.create(
                first_name = first_name,
                last_name = last_name,
                username = username,
                email = broker_email,
                password = make_password(password),
                type = "BROKER"
                )
            print(first_name)
            print(data['phone_number'])
            if user:
                profile = Profile.objects.get(user=user)
                if profile_image == None or len(profile_image) ==0:
                    if 'profile_image' in data:
                        profile_image = data['profile_image']
                        if profile_image == None or len(profile_image) == 0:
                            profile_image = request.FILES.get('profile_image', profile.profile_pic)
                    else:
                        profile_image = profile.profile_pic
                profile.phone_number = data['phone_number']
                profile.address = data['address']
                profile.profile_pic = profile_image
                print(profile.profile_pic)
                profile.save()
                NotificationAction.objects.create(
                    user=user
                )
                
            if profile:
                broker = BrokerProfile.objects.get(profile=profile)
                broker.zuid = zuid
                broker.realtor_profile_url = realtor_profile_url
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
                    "one_time_link":one_time_link,
                    "password": password
                }
            template = "wellcome.html"
            mail_subject = "Wellcome to the RealVision"
            # Please Make Template on Here Email For Broker
            title = "Create Account"
            desc = "Broker account successfully created"
            notification_type = "alert"
            LasUser = User.objects.all().last()
            #print("LasUser=======================================>", LasUser)
            notification_tem(user = LasUser, title = title, desc = desc, notification_type = notification_type)
            print(broker_email, payload, mail_subject)
            # mail_sending(broker_email, payload, template, mail_subject)
            # print(mail_sending)
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
@permission_classes([IsAdminUser])
def batch_create_broker(request):
    data = request.data
    user = request.user
    error = []
    
    batch_data = data['batch_data']
    array_batch_data = json.loads(batch_data.replace("'", "\""))
    print(type(array_batch_data))
    for i in array_batch_data:
        first_name = i['first_name']
        last_name = i['last_name']
        email = i['email']
        phone_number = i['phone_number']
        realtor_profile_url = i['realtor_profile_url']
        profile_image = i['profile_image']
        address = i['address']
        language = i['language']
        zuid = i['zuid']
        if len(zuid) == 0 or zuid == "None":
            zuid = None
        
        if realtor_profile_url is not None:
            if len(realtor_profile_url) == 0 or realtor_profile_url == "None":
                realtor_profile_url = None
                
        broker_email = email
        print(broker_email)
        username = auto_user(broker_email)
        password = "123456"
        
        # print(profile_image, "--------------------Profile Image")
        # print(data['profile_image'])
        # print(input("--------------------->"))
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
                if profile_image == None or len(profile_image) ==0:
                    if profile_image is not None and len(profile_image) > 2:
                        profile_image = profile_image
                    else:
                        profile_image = profile.profile_pic
                profile.phone_number = phone_number
                profile.address = address
                profile.profile_pic = profile_image
                print(profile.profile_pic)
                profile.save()
                NotificationAction.objects.create(
                    user=user
                )
                
            if profile:
                broker = BrokerProfile.objects.get(profile=profile)
                broker.zuid = zuid
                broker.realtor_profile_url = realtor_profile_url
                broker.language = language
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
                    "one_time_link":one_time_link,
                    "password": password
                }
            template = "wellcome.html"
            mail_subject = "Wellcome to the RealVision"
            # Please Make Template on Here Email For Broker
            title = "Create Account"
            desc = "Broker account successfully created"
            notification_type = "alert"
            LasUser = User.objects.all().last()
            #print("LasUser=======================================>", LasUser)
            notification_tem(user = LasUser, title = title, desc = desc, notification_type = notification_type)
            print(broker_email, payload, mail_subject)
            # mail_sending(broker_email, payload, template, mail_subject)
            # print(mail_sending)
        except IntegrityError as e:
            error_message = str(e)
            error = []
            if 'email' in error_message:
                error.append({"email":'user with this Email already exists'})
            if 'username' in error_message:
                error.append({'error':'user with this Username already exists'})
            if 'phone_number' in error_message:
                error.append({'error':'user with this Phone Number already exists'})
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
    return Response({"message": "All Broker Add Successfully "}, status = status.HTTP_200_OK)




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


