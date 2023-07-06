# from django.shortcuts import render
from algorithm.auto_password_generator import generate_password
from authentication.serializers.base_auth import (IpAddress,
                                                  IpAddressSerializer,
                                                  UserSerializerWithToken)
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
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

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def post_ip(request):
    user = request.user
    data = request.data
    if 'ip' not in data:
        return Response({"error": "enter your ip address"}, status=status.HTTP_400_BAD_REQUEST)
    ip_qs = IpAddress.objects.filter(user=user)
    ip_address = data['ip']
    if not ip_qs.exists():
        return Response({"error": "User not Create IP Address"}, status=status.HTTP_400_BAD_REQUEST)
    ip = ip_qs.first()
    ip.ip_address = ip_address
    ip.save()
    return Response({"message": "pass successfully"}, status=status.HTTP_200_OK)