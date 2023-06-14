import time
from datetime import datetime, timedelta

from account.models import BrokerProfile, FreelancerProfile
from algorithm.auto_detect_freelancer import auto_detect_freelancer
from algorithm.OpenAI.get_details_from_openai import get_details_from_openai
from algorithm.send_mail import mail_sending
from common.models.address import SellHouseAddress
from django.contrib.auth import get_user_model
from notifications.models import Notification
from notifications.notification_temp import notification_tem
from order.models import (Amount, BugReport, Commition, DiscountCode, MaxOrder,
                          Order)
from order.serializers import OrderSerializer
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from upload_video.serializer import Video, VideoSerializer


# Create your views here.
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def freelancer_order_delivery(request, order_id):
    user = request.user
    data = request.data
    error = []
    if 'video_title' not in data:
        error.append({"error": "enter your video title"})
    subtitle = request.FILES.get('subtitle')
    video_file = request.FILES.get('video_file')
    if video_file == None:
        error.append({"error": "please attach video file."})
    if user.type == "FREELANCER":
        freelancer = FreelancerProfile.objects.get(profile__user=user)
        order_qs = Order.objects.filter(order_receiver=freelancer, _id=order_id, status="in_progress")
        if not order_qs.exists():
            return Response({"message": "Order is Empty"}, status=status.HTTP_200_OK)
        order = order_qs.first()
        if order.apply_subtitle == True:
            if subtitle == None:
                error.append({"error": "client want subtitle. Please attach subtitle"})
        if len(error) > 0:
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        if order.demo_video == False:
            if order.payment_status == True:
                privacy_type = "public"
        broker = order.order_sender
        broker_orders = Order.objects.all().filter(order_sender = broker)
        if not broker_orders.exists():
            video_demo = True
        else:
            video_demo = False
        video = Video.objects.create(
            order = order,
            video_title = data['video_title'],
            subtitle = subtitle,
            video_file = video_file,
            privacy_type = privacy_type,
            is_demo = video_demo
        )
        if video:
            # use email and notification to broker (for email use template Media your video is ready)
            if order.demo_video == True:
                order.status = "demo"
            else:
                order.status = "completed"
            freelancer = order.order_receiver
            broker.active_orders -= 1
            broker.total_orders += 1
            broker.save()
            freelancer.active_work -= 1
            freelancer.total_work += 1
            freelancer.total_revenue += 20
            freelancer.pending_earn += 20
            order.save()
            freelancer.save()
            broker_email = broker.profile.email
            freelancer_email = freelancer.profile.email
            #Order Complete message to broker and freelancer both mail and notification (template name RealVision Order Completed)
            return Response({"message": "Your Video are now in review by client. Please wait . "}, status=status.HTTP_200_OK)
        return Response({"message": "Your video not Created . Please do it again"}, status=status.HTTP_400_BAD_REQUEST)
    return Response({"error": "You are not Authorize to do this work"}, status=status.HTTP_400_BAD_REQUEST)