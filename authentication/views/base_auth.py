# from django.shortcuts import render
from account.models import Profile
from algorithm.auto_password_generator import generate_password
from algorithm.send_mail import mail_sending
from authentication.serializers.base_auth import (IpAddress,
                                                  IpAddressSerializer,
                                                  UserSerializerWithToken)
from decouple import config
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.shortcuts import redirect
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

# Create your views here.
User = get_user_model()


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        serializer = UserSerializerWithToken(self.user).data
        for key, value in serializer.items():
            data[key] = value
        return data


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def change_password(request):
    data = request.data
    user = request.user
    qs = User.objects.filter(username = user.username)
    if not qs.exists():
        return Response({"error": "You are not Authorize For Changing Password"}, status=status.HTTP_401_UNAUTHORIZED)
    current_user = qs.first()
    if 'password' not in request.POST:
        password = current_user.password
    else:
        password = make_password(data['password'])
        if len(data['password']) < 2:
            password = current_user.password

    current_user.password = password
    current_user.save()
    return Response({"message": "Password Change Successfully"}, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAdminUser])
def resend_password(request, user_id):
    qs = User.objects.filter(id = user_id)
    if not qs.exists():
        return Response({"error": "user Not Exist"}, status=status.HTTP_400_BAD_REQUEST)
    user = qs.first()
    password = generate_password()
    user.password = make_password(password)
    print("Password is ", password)
    user.save()
    #Email
    # email = user.email 
    return Response({"message": "Password Change Successfully"}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def admin_login(request):
    data = request.data
    if 'username' not in data:
        return Response({"error": "Please Enter Username."}, status=status.HTTP_400_BAD_REQUEST)
    username = data['username']
    qs = User.objects.filter(username = username)
    if not qs.exists():
        return Response({"error": "user Not Exist"}, status=status.HTTP_400_BAD_REQUEST)
    user = qs.first()
    serializer = UserSerializerWithToken(user, many=False)
    return Response(serializer.data, status=status.HTTP_200_OK)


# @api_view(['GET'])
# @permission_classes([])
# def test(request):
#     profile = Profile.objects.get(id=4)
#     profile.profile_pic = "https://photos.zillowstatic.com/h_n/ISyrn0hhfo3ll11000000000.jpg"
#     profile.save()
#     return Response("Working")


@api_view(['GET'])
@permission_classes([])
def auto_login(request, email):
    data = request.data
    qs = User.objects.filter(email = email)
    if not qs.exists():
        return Response({"error": "user Not Exist"}, status=status.HTTP_400_BAD_REQUEST)
    user = qs.first()
    ip_domain = config('DOMAIN')
    try:
        token_qs = RefreshToken.for_user(user)
        token = str(token_qs.access_token)
        print(token)
    except:
        token = ""
    # serializer = UserSerializerWithToken(user, many=False)
    # data = serializer.data
    # token = data['token']
    one_time_link = f"{ip_domain}auth?token={token}"
    payload = {
                "one_time_link":one_time_link
    }
    template = "wellcome.html"
    mail_subject = "Wellcome to the RealVision"


    mail_sending(email, payload, template, mail_subject)
    print(mail_sending)
    return redirect (f"https://app.realvisionmedia.com/auth?token={token}")
    # return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def post_ip(request):
    user = request.user
    data = request.data
    if 'ip' not in data:
        return Response({"error": "enter your ip address"}, status=status.HTTP_400_BAD_REQUEST)
    ip_address = data['ip']
    ip_add = IpAddress.objects.create(
        user= user,
        ip_address = ip_address
    )
    return Response({"message": "pass successfully"}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_ip(request):
    user = request.user
    try:
        ip_add = IpAddress.objects.all().filter(user=user)
    except:
        return Response({"error": "No Data Found"}, status=status.HTTP_400_BAD_REQUEST)
    serializer = IpAddressSerializer(ip_add, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_user(request, email):
    user_qs = User.objects.filter(email=email)
    if not user_qs.exists():
        return Response({'error': 'User Not Found'}, status=status.HTTP_400_BAD_REQUEST)
    user = user_qs.first()
    user.delete()
    return Response({"message": "Delete Successfully"}, status=status.HTTP_200_OK)