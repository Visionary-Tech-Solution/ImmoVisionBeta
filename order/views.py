from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

# Create your views here.
from account.models import BrokerProfile, FreelancerProfile, Profile
from account.serializers.base import ProfileSerializer
from account.serializers.broker import BrokerProfileSerializer
from account.serializers.freelancer import FreelancerProfileSerializer
from algorithm.auto_detect_freelancer import auto_detect_freelancer
from order.models import Amount, BugReport, Commition, DiscountCode, Order

User = get_user_model()

@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_amount(request):
    user = request.user
    data = request.data
    if user.is_staff:
        if 'amount' not in request.POST:
            return Response({"error": "enter amount"}, status=status.HTTP_400_BAD_REQUEST)
        amount = Amount.objects.create(
            user = user,
            amount = data['amount']
        )
        return Response({"error": "Amount Update Successfully"}, status=status.HTTP_200_OK)
    return Response({"error": "You are not Authenticate to do this work"}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    user = request.user
    data = request.data
    get_amount = Amount.objects.latest('id')
    amount = int(get_amount.amount)
    error = []
    if 'url' not in request.POST:
        error.append({"error": "enter your url"})

    if 'client_name' not in request.POST:
        error.append({"error": "enter your client name"})

    if 'assistant_type' not in request.POST:
        error.append({"error": "enter your assistant type"})        

    if 'video_language' not in request.POST:
        error.append({"error": "enter your video language"})

    if 'subtitle' not in request.POST:
        error.append({"error": "enter your subtitle"})

    if len(error) > 0:
        return Response(error, status=status.HTTP_400_BAD_REQUEST)

    profiles = FreelancerProfile.objects.all().filter(status_type="active", freelancer_status=True)
    if not profiles.exists():
        return Response({"error": "There is no Data Found For Search"}, status=status.HTTP_400_BAD_REQUEST)
    random_profile = auto_detect_freelancer(profiles)
    return Response({"This is "}, status=status.HTTP_200_OK)