import time

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from account.models import BrokerProfile, FreelancerProfile
from algorithm.auto_detect_freelancer import auto_detect_freelancer
from algorithm.send_mail import mail_sending
from order.models import Amount, BugReport, Commition, DiscountCode, Order
from order.serializers import OrderSerializer

# Create your views here.
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


def pending_order_assign():
    orders = Order.objects.all().filter(status='pending')
    profiles = FreelancerProfile.objects.all().filter(status_type="active", freelancer_status=True)
    if not profiles.exists():
        time.sleep(300)
        pending_order_assign()
    order_assign_profile = auto_detect_freelancer(profiles)
    if len(orders) > 0:
        print(f"pending order -> {orders}")
        if order_assign_profile is not None:
            current_order = orders[0]
            current_order.order_receiver = order_assign_profile
            current_order.status = "assigned"
            current_order.save()
            order_assign_profile.active_work += 1
            order_assign_profile.save()
            return pending_order_assign()
    return True
    


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    user = request.user
    data = request.data
    get_amount = Amount.objects.latest('id')
    amount = int(get_amount.amount)
    broker = BrokerProfile.objects.get(profile__user=user)
    error = []
    if 'url' not in data:
        error.append({"error": "enter your url"})

    if 'client_name' not in data:
        error.append({"error": "enter your client name"})

    if 'assistant_type' not in data:
        error.append({"error": "enter your assistant type"})        

    if 'video_language' not in data:
        error.append({"error": "enter your video language"})

    if 'subtitle' not in data:
        error.append({"error": "enter your subtitle"})

    if len(error) > 0:
        return Response(error, status=status.HTTP_400_BAD_REQUEST)

    profiles = FreelancerProfile.objects.all().filter(status_type="active", freelancer_status=True)
    # profiles = list(profiles)
    if not profiles.exists():
        return Response({"error": "There is no Data Found For Search"}, status=status.HTTP_400_BAD_REQUEST)
    order_assign_profile = auto_detect_freelancer(profiles)
    order = Order.objects.all().filter(order_sender=broker)
    demo_video = False
    payment = True
    if not order.exists():
        demo_video = True
    if order_assign_profile == None:
        status_type = "pending"
    else:
        status_type = "assigned"
    if demo_video == True:
        payment = True
    
    if payment == False:
        return Response({"error": "Payment failed"}, status=status.HTTP_200_OK)
    
    try:
        order = Order.objects.create(
            order_sender = broker,
            url = data['url'],
            client_name = data['client_name'],
            assistant_type = data['assistant_type'],
            video_language = data['video_language'],
            apply_subtitle = data["subtitle"],
            amount = amount,
            status = status_type,
            order_receiver = order_assign_profile,
            demo_video = demo_video,
            order_type = "teaser",
            payment_status = payment
        )
        if order_assign_profile is not None:
            if order:
                #email
                order_assign_profile.active_work += 1
                order_assign_profile.save()
        serializer = OrderSerializer(order, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except:
        return Response({"error": "Server Problem"}, status=status.HTTP_400_BAD_REQUEST)

