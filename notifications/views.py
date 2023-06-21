# from authentication.serializers import UserSerializerWithToken
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from account.models import BrokerProfile, FreelancerProfile, Profile
from account.serializers.base import ProfileSerializer
from account.serializers.broker import BrokerProfileSerializer
from account.serializers.freelancer import FreelancerProfileSerializer
from algorithm.auto_detect_freelancer import auto_detect_freelancer
from algorithm.send_mail import mail_sending
from authentication.models import User
from notifications.models import ContactUs, NotificationAction
from notifications.notification_temp import notification_tem

from .models import Notification
from .serializer import notificationSerializer


class NotificationView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):

        print("NotiUser=============================", request.user)
        
        data = Notification.objects.filter(user=request.user)
        if data:
            serializer = notificationSerializer(data, many=True)

            return Response(
                {
                    'data': serializer.data,
                    'message': "Data fetch"
                },
                status=status.HTTP_302_FOUND
            )
        else:
            return Response(
                {
                    'data': {},
                    'message': "Notification not found"
                },
                status=status.HTTP_204_NO_CONTENT
            )
        


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def action_ready_video(request):
    user = request.user
    notification_alert_qs = NotificationAction.objects.filter(user=user)
    if not notification_alert_qs.exists():
        return Response({"error": "You are not allow for get notification alert"})
    notification_alert = notification_alert_qs.first()
    print(notification_alert.video_ready_alert)
    if notification_alert.video_ready_alert == True:
        notification_alert.video_ready_alert = False
    else:
        notification_alert.video_ready_alert = True
    print(notification_alert.video_ready_alert)
    notification_alert.save()
    return Response({"message": f"Video Ready Aleart Change Successfully"}, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def action_send_offer(request):
    user = request.user
    notification_alert_qs = NotificationAction.objects.filter(user=user)
    if not notification_alert_qs.exists():
        return Response({"error": "You are not allow for get notification alert"})
    notification_alert = notification_alert_qs.first()
    print(notification_alert.offer_alert)
    if notification_alert.offer_alert == True:
        notification_alert.offer_alert = False
    else:
        notification_alert.offer_alert = True
    print(notification_alert.offer_alert)
    notification_alert.save()
    return Response({"message": f"Offer Aleart Change Successfully"}, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def action_blog_post(request):
    user = request.user
    notification_alert_qs = NotificationAction.objects.filter(user=user)
    if not notification_alert_qs.exists():
        return Response({"error": "You are not allow for get notification alert"})
    notification_alert = notification_alert_qs.first()
    print(notification_alert.blog_post_alert)
    if notification_alert.blog_post_alert == True:
        notification_alert.blog_post_alert = False
    else:
        notification_alert.blog_post_alert = True
    print(notification_alert.blog_post_alert)
    notification_alert.save()
    return Response({"message": f"Blog Post Aleart Change Successfully"}, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def action_ai_docs_ready(request):
    user = request.user
    notification_alert_qs = NotificationAction.objects.filter(user=user)
    if not notification_alert_qs.exists():
        return Response({"error": "You are not allow for get notification alert"})
    notification_alert = notification_alert_qs.first()
    print(notification_alert.ai_document_ready_alert)
    if notification_alert.ai_document_ready_alert == True:
        notification_alert.ai_document_ready_alert = False
    else:
        notification_alert.ai_document_ready_alert = True
    print(notification_alert.ai_document_ready_alert)
    notification_alert.save()
    return Response({"message": f"AI Document Ready Aleart Change Successfully"}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def help_me_mail(request):
    user = request.user
    data = request.data
    if user.is_staff:
        return Response({"error": "You are not Authorize for getting Help"}, status=status.HTTP_400_BAD_REQUEST)
    error = []
    if 'subject' not in data:
        error.append({"error": "Please Write Subject "})
    if 'description' not in data:
        error.append({"error": "Please Write Description"})
    if len(error) > 0:
        print(error)
        return Response(error, status=status.HTTP_204_NO_CONTENT)
    subject = data['subject']
    description = data['description']
    print(request.user)
    contact_us = ContactUs.objects.create(
        user=user,
        subject = subject,
        description = description,
        file = request.FILES.get('help_file', None)
    )
    admin_qs = User.objects.filter(is_staff=True)
    admin = admin_qs.first()
    if contact_us:
        notification_tem(user = admin, title = f"Contact Notifcation", desc = f"You user need a help from u. please get details check ur help box {contact_us.id} .", notification_type = "help")
    return Response({"message":"Message Sent Successfully. Please Wait Some time for getting response from Admin."})