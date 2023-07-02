import os
import time
from datetime import datetime, timedelta
from pathlib import PureWindowsPath

from account.models import BrokerProfile, FreelancerProfile
from algorithm.send_mail import mail_sending
from algorithm.watermarkalgo import video_watermark
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from notifications.models import Notification, NotificationAction
from notifications.notification_temp import notification_tem
from order.models import BugReport, Commition, Order
from order.serializers import BugReportSerializer
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from upload_video.serializer import Video, VideoSerializer

# Create your views here.
# ----------------------------------Freelancer-------------------------------------------


# @api_view(['PUT'])
# @permission_classes([IsAuthenticated])
# def freelancer_order_delivery(request, order_id):
#     user = request.user
#     data = request.data
#     get_commition = Commition.objects.latest('id')
#     commition = int(get_commition.commition)
#     wtqs = VideoWatermarkImage.objects.latest('id')
#     watermark = wtqs.watermark
#     error = []
#     current_time = timezone.now()
#     video_file = request.FILES.get('video_file')
#     if video_file == None:
#         error.append({"error": "please attach video file."})
#     if user.type == "FREELANCER":
#         freelancer = FreelancerProfile.objects.get(profile__user=user)
#         order_qs = Order.objects.filter(order_receiver=freelancer, _id=order_id, status="in_progress")
#         if not order_qs.exists():
#             return Response({"message": "Order is Empty"}, status=status.HTTP_200_OK)
#         order = order_qs.first()
#         if len(error) > 0:
#             return Response(error, status=status.HTTP_400_BAD_REQUEST)
#         if order.demo_video == False:
#             if order.payment_status == True:
#                 privacy_type = "public"
#             else:
#                 privacy_type = "private"
#         else:
#             privacy_type = "private"
#         broker = order.order_sender
#         broker_orders = Order.objects.all().filter(order_sender = broker)
#         output_path = os.path.join('orders/watermark_videos/', f'{order._id}watermark.mp4')
#         if not broker_orders.exists():
#             video_demo = True
#         else:
#             video_demo = False
#         try:
#             video = Video.objects.create(
#                 order = order,
#                 video_title = order.order_sender.profile.address,
#                 video_file = video_file,
#                 privacy_type = privacy_type,
#                 is_demo = video_demo
#             )
#             if order.payment_status == False:
#                 video_file_dir = video.video_file
#                 video_watermark(video_file_dir.path, output_path, watermark)
                
#                 video.watermark_video_file = output_path
#                 video.save()
#             video= True
#         except:
#             return Response({"error": "Video Upload Failed"}, status=status.HTTP_400_BAD_REQUEST)
#         if video:
            
#             try:
#                 if current_time > order.order_assign_time + timezone.timedelta(hours=2):
#                     freelancer.late_task += 1
#                     freelancer.save()
#             except Exception as e:
#                 print(e)
#             # use email and notification to broker (for email use template Media your video is ready)
#             broker_user = broker.profile.user
            

#             #notification
#             title = f"Order is ready"
#             desc = f"Your order {order_id} is ready"
#             notification_type = 'alert'
#             try:
#                 notification_alert = NotificationAction.objects.get(user=broker_user)

#             except:
#                 notification_alert = True
#             try:
#                 if notification_alert.video_ready_alert == True:
#                     notification_tem(user=broker_user, title=title, desc=desc, notification_type=notification_type)
#             except Exception as e:
#                 print(e)

#             if order.demo_video == True:
#                 order.status = "demo"

#             else:
#                 order.status = "completed"
#             freelancer = order.order_receiver


#             freelancer_user = freelancer.profile.user


#             broker.active_orders -= 1
#             broker.total_orders += 1
#             broker.save()
#             freelancer.active_work -= 1
#             freelancer.total_work += 1
#             freelancer.total_revenue += int(commition)
#             freelancer.pending_earn -= int(commition)
#             print(freelancer.pending_earn)
#             print(freelancer.total_revenue)
#             order.delivery_time = current_time
#             order.save()
#             print(freelancer.pending_earn)
#             print(freelancer.total_revenue)
#             freelancer.save()
#             broker_email = broker.profile.email
#             freelancer_email = freelancer.profile.email
#             #you got paid
#             #Order Complete message to freelancer both mail and notification (template name RealVision Order Completed)
#             payload = {
#                 "payment_history_link":"www.facebook.com"
#             }
#             template = "you_got_paid_template.html"
#             mail_subject = "You got paid"

#             try:
#                 mail_sending(freelancer_email, payload, template, mail_subject)
#             except Exception as e:
#                 return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

#             try:
#                 notification_tem(user=freelancer_user, title="Paid", desc="You Got Paid", notification_type="alert")

#             except Exception as e:
#                 return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

#             return Response({"message": "Your Video are now in review by client. Please wait."}, status=status.HTTP_200_OK)
#         return Response({"message": "Your video not Created . Please do it again"}, status=status.HTTP_400_BAD_REQUEST)
#     return Response({"error": "You are not Authorize to do this work"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def freelancer_order_delivery(request, order_id):
    user = request.user
    data = request.data
    get_commition = Commition.objects.latest('id')
    commition = int(get_commition.commition)
    error = []
    current_time = timezone.now()
    video_file = request.FILES.get('video_file')
    if video_file == None:
        error.append({"error": "please attach video file."})
    if user.type == "FREELANCER":
        freelancer = FreelancerProfile.objects.get(profile__user=user)
        order_qs = Order.objects.filter(order_receiver=freelancer, _id=order_id, status="in_progress")
        if not order_qs.exists():
            return Response({"message": "Order is Empty"}, status=status.HTTP_200_OK)
        order = order_qs.first()
        if len(error) > 0:
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        if order.demo_video == False:
            if order.payment_status == True:
                privacy_type = "public"
            else:
                privacy_type = "private"
        else:
            privacy_type = "private"
        broker = order.order_sender
        broker_orders = Order.objects.all().filter(order_sender = broker)
        output_filename = f'{order._id}watermark.mp4'
        output_directory = os.path.join(settings.MEDIA_ROOT, PureWindowsPath('orders', 'watermark_videos'))
        output_path = os.path.join(output_directory, output_filename)
        output2_directory = os.path.join(PureWindowsPath('orders', 'watermark_videos'))
        output2_path = os.path.join(output2_directory, output_filename)

        # Create the directory if it doesn't exist
        os.makedirs(output_directory, exist_ok=True)
        if not broker_orders.exists():
            video_demo = True
        else:
            video_demo = False
        video = Video.objects.create(
            order = order,
            video_title = order.order_sender.profile.address,
            video_file = video_file,
            privacy_type = privacy_type,
            is_demo = video_demo
        )
        if order.payment_status == False:
            video_file_dir = video.video_file
            video_watermark(video_file_dir.path, output_path)
            
            video.watermark_video_file = output2_path
            video.save()
        video= True
        if video:
            
            try:
                if current_time > order.order_assign_time + timezone.timedelta(hours=2):
                    freelancer.late_task += 1
                    freelancer.save()
            except Exception as e:
                print(e)
            # use email and notification to broker (for email use template Media your video is ready)
            broker_user = broker.profile.user
            

            #notification
            title = f"Order is ready"
            desc = f"Your order {order_id} is ready"
            notification_type = 'alert'
            try:
                notification_alert = NotificationAction.objects.get(user=broker_user)

            except:
                notification_alert = True
            try:
                if notification_alert.video_ready_alert == True:
                    notification_tem(user=broker_user, title=title, desc=desc, notification_type=notification_type)
            except Exception as e:
                print(e)

            if order.demo_video == True:
                order.status = "demo"

            else:
                order.status = "completed"
            freelancer = order.order_receiver


            freelancer_user = freelancer.profile.user


            broker.active_orders -= 1
            broker.total_orders += 1
            broker.save()
            freelancer.active_work -= 1
            freelancer.total_work += 1
            freelancer.total_revenue += int(commition)
            freelancer.pending_earn -= int(commition)
            print(freelancer.pending_earn)
            print(freelancer.total_revenue)
            order.delivery_time = current_time
            order.save()
            print(freelancer.pending_earn)
            print(freelancer.total_revenue)
            freelancer.save()
            broker_email = broker.profile.email
            freelancer_email = freelancer.profile.email
            #you got paid
            #Order Complete message to freelancer both mail and notification (template name RealVision Order Completed)
            payload = {
                "payment_history_link":"www.facebook.com"
            }
            template = "you_got_paid_template.html"
            mail_subject = "You got paid"

            try:
                mail_sending(freelancer_email, payload, template, mail_subject)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

            try:
                notification_tem(user=freelancer_user, title="Paid", desc="You Got Paid", notification_type="alert")

            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

            return Response({"message": "Your Video are now in review by client. Please wait."}, status=status.HTTP_200_OK)
        return Response({"message": "Your video not Created . Please do it again"}, status=status.HTTP_400_BAD_REQUEST)
    return Response({"error": "You are not Authorize to do this work"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def review_order_delivery(request, order_id):
    user = request.user
    data = request.data
    error = []
    video_file = request.FILES.get('video_file')
    if video_file == None:
        error.append({"error": "please attach video file."})
    if user.type == "FREELANCER":
        freelancer = FreelancerProfile.objects.get(profile__user=user)
        order_qs = Order.objects.filter(order_receiver=freelancer, _id=order_id, status="in_review")
        if not order_qs.exists():
            return Response({"message": "Order is Empty"}, status=status.HTTP_200_OK)
        order = order_qs.first()
        if len(error) > 0:
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        if order.demo_video == False:
            if order.payment_status == True:
                privacy_type = "public"
            else:
                privacy_type = "private"
        else:
            privacy_type = "private"
        broker = order.order_sender
        video = Video.objects.get(order=order)
        video.video_title = order.order_sender.profile.address
        video.privacy_type = privacy_type
        video.video_file = video_file
        video.save()
        email = broker.profile.email
        payload = {
            "video_link":"facebook.com"
        }
        template = "video_is_ready_template.html"
        title = "Your video is ready"
        mail_subject = title
        desc = {

        }

        notification_type = 'alert'


        try:
            mail_sending(email, payload, template, mail_subject)
        except Exception as e:
            Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        try:
            notification_alert = NotificationAction.objects.get(uesr=user)
        except:
            notification_alert = True
        try:
            if notification_alert.video_ready_alert==True:
                notification_tem(user, title, desc, notification_type)
        except Exception as e:
            print(e)

        # use email and notification to broker (for email use template Media your video is ready)
        if order.demo_video == True:
            order.status = "demo"
        else:
            order.status = "completed"
        freelancer = order.order_receiver
        order.save()
        broker_email = broker.profile.email
        freelancer_email = freelancer.profile.email
        #Order Complete message to broker and freelancer both mail and notification (template name RealVision Order Completed)
        return Response({"message": "Your Video are deivery done. "}, status=status.HTTP_200_OK)
    return Response({"error": "You are not Authorize to do this work"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def freelancer_reports(request):
    user = request.user
    if user.type == "FREELANCER":
        freelancer = FreelancerProfile.objects.get(profile__user=user)
        bug_report = BugReport.objects.all().filter(order__order_receiver = freelancer, order__status = "in_review")
        if not bug_report.exists():
            return Response({"message": "No Review Order Exist"}, status=status.HTTP_200_OK)
        serializer = BugReportSerializer(bug_report, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response({"message": "You are not Authorize to see this api"}, status=status.HTTP_400_BAD_REQUEST)

#comment


# ----------------------------------Broker-------------------------------------------

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def broker_reports(request):
    user = request.user
    if user.type == "BROKER":
        broker = BrokerProfile.objects.get(profile__user=user)
        bug_report = BugReport.objects.all().filter(order__order_sender = broker, order__status = "in_review")
        if not bug_report.exists():
            return Response({"message": "No Review Order Exist"}, status=status.HTTP_200_OK)
        serializer = BugReportSerializer(bug_report, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response({"message": "You are not Authorize to see this api"}, status=status.HTTP_400_BAD_REQUEST) 


@api_view(['GET'])
# @permission_classes([])
def all_videos(request):
    video = Video.objects.all()
    serializer = VideoSerializer(video, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)