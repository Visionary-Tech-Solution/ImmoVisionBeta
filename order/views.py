import json
import os
import time
from datetime import date, datetime, timedelta

import stripe
from decouple import config
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import connection
from django.db.models import Q
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from account.models import (BrokerProfile, FreelancerProfile, PaymentMethod,
                            Profile)
from account.serializers.payment import (FreelancerPaymentMethod,
                                         FreelancerPaymentMethodSerializer,
                                         FreelancerWithdraw,
                                         FreelancerWithdrawSerializer)
from algorithm.auto_detect_freelancer import auto_detect_freelancer
from algorithm.datetime_to_day import get_day_from_datetime, get_day_name
from algorithm.OpenAI.get_details_from_openai import get_details_from_openai
from algorithm.send_mail import mail_sending
from common.models.address import SellHouseAddress
from notifications.models import Notification, NotificationAction
from notifications.notification_temp import notification_tem
from order.models import (Amount, BugReport, Commition, DiscountCode, MaxOrder,
                          Order)
from order.serializers import (AggregatedDataSerializer,
                               DiscountCodeSerializer, OrderSerializer)
from upload_video.models import Video

# Create your views here.
User = get_user_model()
stripe.api_key  = config('STRIPE_SECRET_KEY')
publish_key = config('STRIPE_PUBLISHABLE_KEY')
# -------------------------------Order Base Function------------------------------------- 
def get_paginated_queryset_response(qs, request):
    paginator = PageNumberPagination()
    paginator.page_size = 15
    paginated_qs = paginator.paginate_queryset(qs, request)
    total_pages = paginator.page.paginator.num_pages
    serializer = OrderSerializer(paginated_qs, many=True)
    return paginator.get_paginated_response({
        'total_pages': total_pages,
        'current_page': paginator.page.number,
        'data': serializer.data,
})

def get_paginated_queryset_response_for_withdraw(qs, request):
    paginator = PageNumberPagination()
    paginator.page_size = 10
    paginated_qs = paginator.paginate_queryset(qs, request)
    total_pages = paginator.page.paginator.num_pages
    serializer = FreelancerWithdrawSerializer(paginated_qs, many=True)
    return paginator.get_paginated_response({
        'total_pages': total_pages,
        'current_page': paginator.page.number,
        'data': serializer.data,
})



#pending Order Assign Freelancer
def pending_order_assign():
    orders = Order.objects.all().filter(status='pending')
    print("pending order run ..")
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
            order_assign_profile.active_work += 1
            current_order.order_assign_time = datetime.now().time()
            current_order.save()
            order_assign_profile.save()
            broker_email = current_order.order_sender.profile.email
            freelancer_email = current_order.order_receiver.profile.email
            receiver_name = current_order.order_receiver.profile.username
            order_id = current_order._id
            print(broker_email, freelancer_email)

            broker_pending_order_subject = f"Order Confirm and your order assign on {receiver_name}"
            freelancer_pending_order_subject = "You got a new task. Please do this work first."
            freelancer = current_order.order_receiver
            notification_tem(user=freelancer.profile.user, title=freelancer_pending_order_subject, desc=f"Your Got an Order.  Please Do This work fast {order_id}", notification_type='order')

            #broker
            payload = {
                "order_id":order_id
            }
            # pending_order_broker_template = "pending_order_broker_template.html"
            pending_order_freelancer_template = "freelancer_got_task.html"
            freelancer_payload = {
                    "task_link" : f"{config('DOMAIN')}editor/my-tasks",
                    "property_image": current_order.property_photo_url,
                }
            # try:
                # mail_sending(broker_email, payload, pending_order_broker_template, broker_pending_order_subject)
                # pass
            # except Exception as e:
            #     return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                mail_sending(freelancer_email, freelancer_payload, pending_order_freelancer_template, freelancer_pending_order_subject)
                print(mail_sending, "-----------------------> Mail Done")
            except Exception as e:
                print(e, "Email Problem on Order Confirm")
            #email (Broker) Order Confirm and ur order assign on receiver_name
            #email (Receiver) You got an Order. Please Do This work fast (Order ID pass)
            return pending_order_assign()
    return True


# -------------------------------------Payment Based Function ----------------------------

def charge_customer(customer_id, payment_type, order_id=None):
    # Lookup the payment methods available for the customer
    get_amount = Amount.objects.latest('id')
    amount = 69.99*100
    payment_methods = stripe.PaymentMethod.list(
        customer=customer_id,
        type=payment_type
    )
    # Charge the customer and payment method immediately
    print("----------------------------------------->")
    print(payment_methods, "This is nont")
    try:
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency='usd',
            customer=customer_id,
            payment_method=payment_methods.data[0].id,
            off_session=True,
            confirm=True
        )
        print(intent)
        if order_id is not None:
            order = Order.objects.get(_id=order_id)
            order.payment_status = True
            order.payment_type = payment_type
            order.payment_intent_id = intent['id']
            order.save()
        return Response({
                'clientSecret': intent['client_secret'],
                'publishable_key': publish_key
            }, status=status.HTTP_200_OK)
    except stripe.error.CardError as e:
        err = e.error
        # Error code will be authentication_required if authentication is needed
        print('Code is: %s' % err.code)
        payment_intent_id = err.payment_intent['id']
        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        return Response({
                'payment_intent_id': payment_intent_id,
                'payment_intent': payment_intent
            }, status=status.HTTP_200_OK)
    except:
        return Response({
            "error": "Your Order Can't Possible to create . "
        })



#waiting Order Redirect
def order_waiting():
    orders = Order.objects.all().filter(status="assigned")
    profiles = FreelancerProfile.objects.all().filter(status_type="active", freelancer_status=True)
    print("order waiting run ..")
    get_max_order = MaxOrder.objects.latest('id')
    max_order = int(get_max_order.max_order)
    active_work_profile = profiles.values_list('active_work', flat=True)
    if len(orders) > 0:
        if any(value < max_order for value in list(active_work_profile)):
            for order in orders:
                assign_time = order.order_assign_time
                if assign_time is not None:
                    deadline = (datetime.combine(datetime.today(), assign_time) + timedelta(hours=1)).time()
                    print(f"Assign Time: {assign_time}, Deadline: {deadline}")
                else:
                    deadline = datetime.today()
                if assign_time is not None:
                    if assign_time <= deadline:
                        previous_freelancer = FreelancerProfile.objects.get(profile=order.order_receiver.profile)
                        query = profiles.exclude(profile=previous_freelancer.profile)
                        new_assign = auto_detect_freelancer(query)
                        if new_assign is not None:

                        #notifiy admin that previous freelancer not work perfectly

                            #changes==========================
                            admins = User.objects.filter(is_superuser=True)
                            for admin in admins:
                                notification_tem(user=admin, title="Decline Work", desc=f"Freelancer {order.order_sender} is not working", notification_type = 'alert')

                            if previous_freelancer.active_work > 0:
                                previous_freelancer.active_work -= 1
                            else:
                                previous_freelancer.active_work = 0
                            previous_freelancer.save()
                            order.order_receiver = new_assign
                            notification_tem(user=new_assign.profile.user, title="New Work Detected", desc="You've got new work", notification_type = 'alert')
                            #notifiy New Receiver that He Got new work by Email
                            print(new_assign)
                            print(new_assign.active_work)
                            new_assign.active_work += 1
                            new_assign.save()
                            order.order_assign_time = datetime.now().time()
                            order.save()
                            time.sleep(0.5)


# -----------------------------------------Admin Section ------------------------------------

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
        return Response({"message": "Amount Update Successfully"}, status=status.HTTP_200_OK)
    return Response({"error": "You are not Authenticate to do this work"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_max_order(request):
    user = request.user
    data = request.data
    if user.is_staff:
        if 'max_order' not in data:
            return Response({"error": "enter max order"}, status=status.HTTP_400_BAD_REQUEST)
        max_order = MaxOrder.objects.create(
            user = user,
            max_order = data['max_order']
        )
        return Response({"message": "Max Order Update Successfully"}, status=status.HTTP_200_OK)
    return Response({"error": "You are not Authenticate to do this work"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_commition(request):
    user = request.user
    data = request.data
    if user.is_staff:
        if 'commitin' not in data:
            return Response({"error": "enter commition for editor"}, status=status.HTTP_400_BAD_REQUEST)
        Commition.objects.create(
            user = user,
            commition = data['commitin']
        )
        return Response({"message": "Freelancer Commision Update Successfully"}, status=status.HTTP_200_OK)
    return Response({"error": "You are not Authenticate to do this work"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def all_orders(request):
    status_type_query = request.query_params.get('status_type') 
    email_query = request.query_params.get('email') 
    try:
        orders = Order.objects.all().order_by('-created_at')
    except:
        return Response({"error": "Server Error"}, status=status.HTTP_400_BAD_REQUEST)
    if status_type_query:
        orders = orders.filter(status=status_type_query)
    if email_query:
        email_query = email_query.lower()
        orders = orders.filter(Q(order_receiver__profile__email=email_query) | Q(order_sender__profile__email=email_query))
    return get_paginated_queryset_response(orders, request)
    

@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_discount_coupon(request):
    user = request.user
    data = request.data
    error = []
    if 'code' not in data:
        error.append({"error": "enter your code"})
    
    if 'valid_date' not in data:
        error.append({"error": "enter deadline"})
    
    
    if 'discount_percentage' not in data:
        error.append({"error": "enter discount percentage in this coupon"})
    
    if len(error) > 0:
        return Response(error, status=status.HTTP_400_BAD_REQUEST)
    discount_coupon = DiscountCode.objects.create(
        user = user,
        code = data['code'],
        valid_date = data['valid_date'],
        discount_percentage = data['discount_percentage']
    )
    serializer = DiscountCodeSerializer(discount_coupon, many=False)
    return Response(serializer.data, status=status.HTTP_201_CREATED)



@api_view(['PUT'])
@permission_classes([IsAdminUser])
def update_discount_coupon(request, discount_code_id):
    user = request.user
    data = request.data
    discount_code_qs = DiscountCode.objects.filter(_id = discount_code_id)
    if not discount_code_qs:
        return Response({"error": "Discount Code Not Exist"}, status=status.HTTP_400_BAD_REQUEST)
    discount_code = discount_code_qs.first()
    code = discount_code.code
    if 'code' in request.POST:
        code = data['code']
        if len(code) < 2:
            code = discount_code.code
    
    valid_date = discount_code.valid_date
    if 'valid_date' in request.POST:
        valid_date = data['valid_date']
        if len(valid_date) < 2:
            valid_date = discount_code.valid_date
    
    if 'discount_percentage' in request.POST:
        discount_percentage = data['discount_percentage']
        if len(discount_percentage) < 2:
            discount_percentage = discount_code.discount_percentage
    
    discount_code.code = code
    discount_code.valid_date = valid_date
    discount_code.discount_percentage = discount_percentage
    discount_code.save()
    return Response({"message": "Discount Coupon Update Successfully"}, status=status.HTTP_201_CREATED)

@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_discount_coupon(request, discount_code_id):
    discount_code_qs = DiscountCode.objects.filter(_id = discount_code_id)
    if not discount_code_qs:
        return Response({"error": "Discount Code Not Exist"}, status=status.HTTP_400_BAD_REQUEST)
    discount_code = discount_code_qs.first()
    discount_code.delete()
    return Response({"message": "Discount Coupon Delete Successfully"}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def all_discount_coupon(request):
    discount_coupons = DiscountCode.objects.all()
    serializer = DiscountCodeSerializer(discount_coupons, many=True)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def all_withdraw_request(request):
    user = request.user
    status_type_query = request.query_params.get('status_type')
    email_query = request.query_params.get('email') 
    if user.is_staff:
        try:
            withdraw_list = FreelancerWithdraw.objects.all().order_by('-created_at')
        except:
            return Response({"error": "Server Error"}, status=status.HTTP_400_BAD_REQUEST)
        if email_query:
            email_query = email_query.lower()
            withdraw_list = withdraw_list.filter(Q(withdraw_method__freelancer__profile__email=email_query))
        if status_type_query:
            status_type_query = status_type_query.lower()
            withdraw_list = withdraw_list.filter(Q(withdraw_status=status_type_query))
        return get_paginated_queryset_response_for_withdraw(withdraw_list, request)
    return Response({'error': 'You are not Authorize'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([IsAdminUser])
def withdraw_confirm(request, id):
    withdraw_request_qs = FreelancerWithdraw.objects.filter(id=id) 
    if not withdraw_request_qs.exists():
        return Response({'error': 'Withdraw Info Not Found or Not Exist'}, status=status.HTTP_400_BAD_REQUEST)
    withdraw_request = withdraw_request_qs.first()
    withdraw_request.withdraw_status = "complete"
    amount = withdraw_request.withdraw_amount
    withdraw_request.save()
    #Order Complete message to freelancer both mail and notification (template name RealVision Order Completed)
    freelancer = withdraw_request.withdraw_method.freelancer.profile
    freelancer_user = freelancer.user
    print(freelancer_user.first_name, "This is the name ")
    payload = {
        "payment_history_link":"www.facebook.com",
        "name":  f"{freelancer_user.first_name} {freelancer_user.last_name}",
        "amount": amount
    }
    template = "you_got_paid_template.html"
    mail_subject = "You got paid"
    freelancer_email = freelancer.email
    try:
        mail_sending(freelancer_email, payload, template, mail_subject)
        print(mail_sending, "---------------------> Mail Send Perfectly")
    except Exception as e:
        print(e, "Email Problem on Got Paid Freelancer")
    try:
        notification_tem(user=freelancer_user, title="Paid", desc="You Got Paid", notification_type="alert") 
    except Exception as e:
        print(e, "Email Problem on Got Paid Freelancer")
    return Response({"message": "Payment Successfully Done"}, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAdminUser])
def withdraw_cancel(request, id):
    withdraw_request_qs = FreelancerWithdraw.objects.filter(id=id, withdraw_status="pending")
    if not withdraw_request_qs.exists():
        return Response({'error': 'Withdraw Info Not Found or Not Exist'}, status=status.HTTP_400_BAD_REQUEST)
    withdraw_request = withdraw_request_qs.first()
    withdraw_request.withdraw_status = "cancel"
    # withdraw_amount
    freelancer = withdraw_request.withdraw_method.freelancer
    withdraw_amount = withdraw_request.withdraw_amount
    freelancer.total_revenue += withdraw_amount
    freelancer.save()
    withdraw_request.save()
    return Response({"message": "Payment Cancel Done"}, status=status.HTTP_200_OK)
# -------------------------------------------------Broker Section---------------------------------

# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def create_order(request):
#     user = request.user
#     print(user)
#     data = request.data
#     get_amount = Amount.objects.latest('id')
#     amount = int(get_amount.amount)
#     if 'discount_code' in request.POST:
#         discount_code = data['discount_code']
#         discount_qs = DiscountCode.objects.filter(code=discount_code)
#         if not discount_qs.exists():
#             return Response({"error": "Discount Code Not Exist"}, status=status.HTTP_400_BAD_REQUEST)
#         discount = discount_qs.first()
#         today = date.today()
#         valid_date = discount.valid_date
#         if today <= valid_date:
#             percentage_amount = (amount / discount.discount_percentage) * 100
#             amount = int(percentage_amount)
#         else:
#             return Response({"error": "Discount Code Date Over"}, status=status.HTTP_400_BAD_REQUEST)
    
#     profile = Profile.objects.get(user = user)
#     payment_type = ""
#     qs = BrokerProfile.objects.filter(profile=profile)
#     if not qs.exists():
#         return Response({"error": "For making order you have to be Broker"}, status=status.HTTP_400_BAD_REQUEST)
#     broker = qs.first()
#     error = []
#     if 'url' not in data:
#         error.append({"error": "enter your url"})
    
#     if 'zpid' not in data:
#         error.append({"error": "enter your zpid"})

#     if 'client_name' not in data:
#         error.append({"error": "enter your client name"})

#     if 'assistant_type' not in data:
#         error.append({"error": "enter your assistant type"})        

#     if 'video_language' not in data:
#         error.append({"error": "enter your video language"})

#     if 'subtitle' not in data:
#         error.append({"error": "enter your subtitle"})
    
#     if 'primary_photo_url' not in data:
#         error.append({"error": "enter your primary photo url"})
#     order = Order.objects.all().filter(order_sender=broker)
#     demo_video = False
#     if not order.exists():
#         demo_video = True
#     if demo_video == False:
#         if 'payment_intent_id' not in data:
#             error.append({"error": "enter your payment intent id"})
        
#         if 'payment_method_id' not in data:
#             error.append({"error": "enter your payment method id"})
        
#         if 'payment_type' not in data:
#             error.append({"error": "enter your payment type"})
        
#         payment_type = data['payment_type']

    
#     # Address ----------------------------------> 
#     if 'line1' not in data:
#         error.append({"error": "enter your line1"})

#     if 'line2' not in data:
#         error.append({"error": "enter your line2"})    

#     if 'state' not in data:
#         error.append({"error": "enter your state"})

#     if 'postalCode' not in data:
#         error.append({"error": "enter your postalCode"})

#     if 'city' not in data:
#         error.append({"error": "enter your city"})

#     if 'latitude' not in request.POST:
#         latitude = None
#     else:
#         latitude = data['latitude']
#     if 'longitude' not in request.POST:
#         longitude = None
#     else:
#         longitude = data['longitude']

    
#     if len(error) > 0:
#         return Response(error, status=status.HTTP_400_BAD_REQUEST)
#     subtitle_txt = data['subtitle']
#     if subtitle_txt =="true":
#         subtitle = True
#     else:
#         subtitle = False
#     profiles = FreelancerProfile.objects.all().filter(status_type="active", freelancer_status=True)
#     # profiles = list(profiles)
#     if not profiles.exists():
#         order_assign_profile = None
#     else:
#         order_assign_profile = auto_detect_freelancer(profiles)
    
#     profile.payment_type = payment_type
#     if 'payment_method_id' and 'payment_intent_id'  in data:
#         payment = True
#     else:
#         payment = False
    
#     if order_assign_profile == None:
#         status_type = "pending"
#     else:
#         status_type = "assigned"
#     if demo_video == True:
#         payment = False
    
#     if payment == False and demo_video is not True:
#         return Response({"error": "Payment failed"}, status=status.HTTP_200_OK)
    
#     property_address = SellHouseAddress.objects.create(
#         line1 = data['line1'],
#         state = data['state'],
#         line2 = data['line2'],
#         postalCode = data['postalCode'],
#         city = data['city'],
#         latitude = latitude,
#         longitude = longitude,
#     )
#     url = data['url']
#     # url = "https://www.dwh.co.uk/campaigns/offers-tailor-made-with-you-in-mind/"
#     details_data = f"https://zillow.com{url}"
#     address = f"{property_address.line1} , {property_address.state}, {property_address.line2}, {property_address.postalCode}, {property_address.city}"
#     try:
#         property_details = get_details_from_openai(details_data)
#     except:
#         property_details = None
#     try:
#         notification_alert = NotificationAction.objects.get(user=user)
#     except:
#         notification_alert = True
#     if notification_alert == True:
#         desc = f"Hello {user}, You New Order AI Document is Ready"
#         notification_tem(user = user, title = "AI Document Ready", desc = desc,notification_type = "alert")
#     if property_address:
#         order = Order.objects.create(
#             order_sender = broker,
#             zpid = data['zpid'],
#             url = url,
#             client_name = data['client_name'],
#             assistant_type = data['assistant_type'],
#             video_language = data['video_language'],
#             apply_subtitle = subtitle,
#             amount = amount,
#             property_address = property_address,
#             property_photo_url = data['primary_photo_url'],
#             property_details = property_details,
#             status = status_type,
#             order_receiver = order_assign_profile,
#             demo_video = demo_video,
#             payment_intent_id = data['payment_intent_id'],
#             payment_method_id = data['payment_method_id'],
#             address = address,
#             order_type = "teaser",
#             payment_status = payment
#         )
#     if order_assign_profile is not None:
#         if order:
#             broker_profile = order.order_sender
#             broker_email = broker_profile.profile.email
#             freelancer_email = order_assign_profile.profile.email
#             print(freelancer_email)
#             broker_profile.active_orders += 1
#             print(broker_email)
#             #email (Broker) Order Confirm and ur order assign on receiver_name
#             #email (Receiver) You got an Order. Please Do This work first (Order ID pass)
#             #broker notification =================
#             title = f"Order Confirm and ur order assign on {order_assign_profile.profileusername}"
#             notification_payload = order._id
#             desc = notification_payload
#             notification_tem(user = request.user, title = title, desc = desc,notification_type = "alert")
#             #reciver notification =================
#             title = f"You got an Order. Please Do This work first"
#             notification_payload = order._id
#             desc = notification_payload
#             notification_tem(user = order_assign_profile.profile.user, title = title, desc= desc, notification_type = "order")
#             order_date = order.created_at
            
#             payload = {
#                 "order_id":order._id,
#                 "order_date":order_date,
#                 #billing info
#                 "home":"Maria Bergamot",
#                 "road_no":"3409 S. Canondale Road",
#                 "area":"Chicago, IL 60301",
#                 "product_name":"Video Property Teaser",
#                 "qty":1,
#                 "amount":order.amount,
#                 "tax":"6",
#                 "order_link":"www.facebook.com"
#             }
#             #templates
#             broker_template = "order_completed.html"
#             freelancer_template = "freelancer_template.html"
#             print("+==================================================>", broker_template)
#             #subjects
#             broker_mail_subject = f"Order Confirm and ur order assign on{order_assign_profile.profile.username}"
#             freelancer_order_mail_subject = f"You got an Order. Please Do This work first"
            
#             #broker
#             try:
#                 mail_sending(broker_email, payload, broker_template, broker_mail_subject)
#             except Exception as e:
#                 return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
#             try:
#                 mail_sending(freelancer_email, payload, freelancer_template,freelancer_order_mail_subject)
#             except Exception as e:
#                 return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
#             print(order_assign_profile)
#             print(order_assign_profile.active_work)
#             order_assign_profile.active_work += 1
#             print(order_assign_profile.active_work)
#             broker_profile.save()
#             order_assign_profile.save()
#             order.order_assign_time = datetime.now().time()
#             order.save()
#     else:
#         #email (Broker) Please wait some time . Very Soon We will Assign a freelancer forcomplete your order
#         broker_mail_subject = "Please wait some time . Very Soon We will Assign afreelancer for complete your order"
#         payload = {}
#         try:
#             mail_sending(broker_email, payload, broker_template, broker_mail_subject)
#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
#     serializer = OrderSerializer(order, many=False)
#     return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([])
def order_details(request, order_id):
    user = request.user
    order_qs = Order.objects.filter(_id=order_id)
    if not order_qs.exists():
        return Response({"error": "Order Not Found"}, status=status.HTTP_400_BAD_REQUEST)
    order = order_qs.first()
    serializer = OrderSerializer(order, many=False)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    user = request.user
    print(user)
    broker_email = user.email
    data = request.data
    get_amount = Amount.objects.latest('id')
    amount = 69.99
    
    if 'discount_code' in request.POST:
        discount_code = data['discount_code']
        discount_qs = DiscountCode.objects.filter(code=discount_code)
        if not discount_qs.exists():
            return Response({"error": "Discount Code Not Exist"}, status=status.HTTP_400_BAD_REQUEST)
        discount = discount_qs.first()
        today = date.today()
        valid_date = discount.valid_date
        if today <= valid_date:
            percentage_amount = (amount / discount.discount_percentage) * 100
            amount = int(percentage_amount)
        else:
            return Response({"error": "Discount Code Date Over"}, status=status.HTTP_400_BAD_REQUEST)
    #templates
    broker_template = "order_completed.html"
    freelancer_template = "freelancer_got_task.html"
    profile = Profile.objects.get(user = user)
    payment_method = PaymentMethod.objects.get(profile=profile)

    payment_type = "demo_vide"
    payment_intent_id = "demo_video"
    payment_method_id = "demo_video"
    qs = BrokerProfile.objects.filter(profile=profile)
    if not qs.exists():
        return Response({"error": "For making order you have to be Broker"}, status=status.HTTP_400_BAD_REQUEST)
    broker = qs.first()
    error = []
    if 'url' not in data:
        error.append({"error": "enter your url"})
    
    if 'zpid' not in data:
        error.append({"error": "enter your zpid"})

    if 'client_name' not in data:
        error.append({"error": "enter your client name"})

    if 'assistant_type' not in data:
        error.append({"error": "enter your assistant type"})        

    if 'video_language' not in data:
        error.append({"error": "enter your video language"})

    if 'subtitle' not in data:
        error.append({"error": "enter your subtitle"})
    
    if 'primary_photo_url' not in data:
        error.append({"error": "enter your primary photo url"})
    order = Order.objects.all().filter(order_sender=broker)
    demo_video = False
    # if not order.exists():
    #     demo_video = True
    #     broker.is_demo = True
    # else:
    #     broker.is_demo = False
    broker.save()
    # if demo_video == False:
    if payment_method.stripe_customer_id == None or len(payment_method.stripe_customer_id )== 0:
        if 'payment_intent_id' not in data:
            error.append({"error": "enter your payment intent id"})
        
        if 'payment_method_id' not in data:
            error.append({"error": "enter your payment method id"})
        
        if 'payment_type' not in data:
            error.append({"error": "enter your payment type"})
    
    # Address ----------------------------------> 
    if 'line1' not in data:
        error.append({"error": "enter your line1"})

    if 'line2' not in data:
        error.append({"error": "enter your line2"})    

    if 'state' not in data:
        error.append({"error": "enter your state"})

    if 'postalCode' not in data:
        error.append({"error": "enter your postalCode"})

    if 'city' not in data:
        error.append({"error": "enter your city"})

    if 'latitude' not in request.POST:
        latitude = None
    else:
        latitude = data['latitude']
    if 'longitude' not in request.POST:
        longitude = None
    else:
        longitude = data['longitude']

    
    if len(error) > 0:
        return Response(error, status=status.HTTP_400_BAD_REQUEST)
    subtitle_txt = data['subtitle']
    if subtitle_txt =="true":
        subtitle = True
    else:
        subtitle = False
    profiles = FreelancerProfile.objects.all().filter(status_type="active", freelancer_status=True)
    # profiles = list(profiles)
    if not profiles.exists():
        order_assign_profile = None
    else:
        order_assign_profile = auto_detect_freelancer(profiles)
    
    profile.payment_type = payment_type
    if 'payment_method_id' and 'payment_intent_id'  in data:
        payment_method_id = data['payment_method_id']
        payment_intent_id = data['payment_intent_id']
    if payment_method.stripe_customer_id is None or len(payment_method.stripe_customer_id) == 0:
        if 'payment_method_id' and 'payment_intent_id'  in data:
            payment_method_id = data['payment_method_id']
            payment_intent_id = data['payment_intent_id']
            payment = True
        else:
            payment = False
    else:
        payment = True
    
    if order_assign_profile == None:
        status_type = "pending"
    else:
        status_type = "assigned"
    if demo_video == False :
        if payment_method.stripe_customer_id is None or len(payment_method.stripe_customer_id) == 0:
            payment_method_id = data['payment_method_id']
            payment_intent_id = data['payment_intent_id']
            payment_type = data['payment_type']
    
    if payment == False and demo_video is not True:
        return Response({"error": "Payment failed"}, status=status.HTTP_200_OK)
    try:
        property_address = SellHouseAddress.objects.create(
            line1 = data['line1'],
            state = data['state'],
            line2 = data['line2'],
            postalCode = data['postalCode'],
            city = data['city'],
            latitude = latitude,
            longitude = longitude,
        )

        url = data['url']
        prompt = "create a 60 seconds Pitch sale in form of text"
        prompt_social_media = "Create me a short description for a facebook post to present this new property and invite people to share this post and find the new owner for this property in 200 character and don't use any emoji"
        details_data = f"https://zillow.com{url}"
        print("This is running ...")
        address = f"{property_address.line1} , {property_address.state}, {property_address.line2}, {property_address.postalCode}, {property_address.city}"
        try:
            property_details = get_details_from_openai(details_data, prompt)
            social_media_post = get_details_from_openai(details_data, prompt_social_media)
        except:
            property_details = None
            social_media_post = None
        try:
            notification_alert = NotificationAction.objects.get(user=user)
        except:
            notification_alert = True
        if notification_alert == True:
            desc = f"Hello {user}, You New Order AI Document is Ready"
            notification_tem(user = user, title = "AI Document Ready", desc = desc, notification_type = "alert")
        if property_address:
            order = Order.objects.create(
                order_sender = broker,
                zpid = data['zpid'],
                url = url,
                client_name = data['client_name'],
                assistant_type = data['assistant_type'],
                video_language = data['video_language'],
                apply_subtitle = subtitle,
                amount = amount,
                social_media_post = social_media_post,
                property_address = property_address,
                property_photo_url = data['primary_photo_url'],
                property_details = property_details,
                status = status_type,
                order_receiver = order_assign_profile,
                demo_video = demo_video,
                payment_intent_id = payment_intent_id,
                payment_method_id = payment_method_id,
                address = address,
                order_type = "teaser",
                payment_status = payment
            )
        if order_assign_profile is not None:
            if order:
                broker_profile = order.order_sender
                broker_email = broker_profile.profile.email
                freelancer = order_assign_profile.profile
                freelancer_email = freelancer.email
                print(freelancer_email)
                broker_profile.active_orders += 1
                print(broker_profile.active_orders)
                #email (Broker) Order Confirm and ur order assign on receiver_name
                #email (Receiver) You got an Order. Please Do This work first (Order ID pass)


                #broker notification =================
                title = f"Your order is Confirmed, Thank you!"
                notification_payload = order._id
                desc = notification_payload
                notification_tem(user = request.user, title = title, desc = desc, notification_type = "order")

                #reciver notification =================
                title = f"You got an Order. Please Do This work first"
                notification_payload = order._id
                desc = notification_payload
                notification_tem(user = order_assign_profile.profile.user, title = title, desc = desc, notification_type = "order")
                order_date = order.created_at
                ip = config('DOMAIN')
                if len(profile.address) > 2 or profile.address is not None:
                    profile_address = profile.address
                else:
                    profile_address = ""
                broker_payload = {
                    "order_id":order._id,
                    "order_date":order_date,
                    "broker_name": f"{user.first_name} {user.last_name}",
                    #billing info
                    "address": profile_address,
                    "property_image": order.property_photo_url,
                    "product_name":"Video Property Teaser",
                    "qty":1,
                    "amount":order.amount,
                    "tax":"0",
                    "order_link":f"{ip}/order_details/{order._id}"
                }

                

                print("+==================================================>", broker_template)

                #subjects
                broker_mail_subject = f"Order Confirmation - Thank you for your purchase!"
                freelancer_order_mail_subject = f"You got a new task. Please do this work first."
                
                #broker
                try:
                    mail_sending(broker_email, broker_payload, broker_template, broker_mail_subject)
                except Exception as e:
                    print(e, "Email Problem On Order Confirm ")
                
                freelancer_payload = {
                    "task_link" : f"{config('DOMAIN')}editor/my-tasks",
                    "property_image": order.property_photo_url,
                    "name" : f"{freelancer.user.first_name} {freelancer.user.last_name}"
                }

                try:
                    mail_sending(freelancer_email, freelancer_payload, freelancer_template, freelancer_order_mail_subject)
                    print(mail_sending, "Freelancer Mail Sending ................>")
                except Exception as e:
                    print(e, "Email Problem On Order Freelancer ")
                
                print(order_assign_profile)
                print(order_assign_profile.active_work)
                order_assign_profile.active_work += 1
                print(order_assign_profile.active_work)
                broker_profile.is_demo = False
                broker_profile.save()
                print(broker_profile.active_orders)
                order_assign_profile.save()
                order.order_assign_time = datetime.now().time()
                order.save()
        else:
            #email (Broker) Please wait some time . Very Soon We will Assign a freelancer for complete your order
            broker_mail_subject = "Please wait some time . Very Soon We will Assign a freelancer for complete your order"
            payload = {}

            # try:
            #     mail_sending(broker_email, payload, broker_template, broker_mail_subject)
            #     pass
            # except Exception as e:
            #     return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
        serializer = OrderSerializer(order, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except:
        return Response({"error": "Server Problem"}, status=status.HTTP_400_BAD_REQUEST)






# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def make_payment(request, order_id):
#     user = request.user
#     data = request.data
#     profile = Profile.objects.filter(user=user)
#     if not profile.exists():
#         return Response({"error": "Profile Not Exist"}, status=status.HTTP_204_NO_CONTENT)
#     error = []
#     get_amount = Amount.objects.latest('id')
#     amount = int(get_amount.amount) * 100
#     if 'payment_method_id' not in data:
#         error.append({"message": "Input your payment method id"})
    
#     if 'last4' not in data:
#         error.append({"message": "Input your last 4 digit"})
    
#     if 'month' not in data:
#         error.append({"message": "Input your expery month"})
    
#     if 'year' not in data:
#         error.append({"message": "Input your expery year"})
    

    
#     payment_method_id = data["payment_method_id"]
#     last4 = data["last4"]
#     month = data["month"]
#     year = data["year"]
#     if payment_method_id == 'new_card':
#             if 'customer_stripe_id' not in data:
#                 error.append({"message": "Input customer stripe id"})
#             customer_stripe_id = data["customer_stripe_id"]
#             add_payment_method(profile, payment_method_id, last4, month, year, customer_stripe_id)
#     if len(error) > 0:
#         return Response( error ,status=status.HTTP_400_BAD_REQUEST)
#     try:
#         intent = stripe.PaymentIntent.create(
#                     amount=amount,  # Amount in cents
#                     currency='usd',
#                     customer=profile.stripe_customer_id,
#                     payment_method=payment_method_id,
#                     off_session=True,
#                     confirm=True,
#                 )
#         if intent:
#             order = Order.objects.get(_id=order_id)
#             order.payment_status = True
#             order.payment_type = payment_method_id
#             order.save()
#             return Response({"message": "Payment Successfully"}, status=status.HTTP_200_OK)
#     except stripe.error.CardError as e:
#         # Handle card error
#         return Response({"error": "card error"}, status=status.HTTP_400_BAD_REQUEST)
#     except stripe.error.InvalidRequestError as e:
#         # Handle invalid request
#         return Response({"error": "invalid request"}, status=status.HTTP_400_BAD_REQUEST)
        
#     except stripe.error.AuthenticationError as e:
#         # Handle authentication error
#         return Response({"error": "authentication error"}, status=status.HTTP_400_BAD_REQUEST)
        
#     except stripe.error.APIConnectionError as e:
#         # Handle API connection error
#         return Response({"error": "API connection error"}, status=status.HTTP_400_BAD_REQUEST)
        
#     except stripe.error.StripeError as e:
#         # Handle other Stripe errors
#         return Response({"error": "Stripe errors"}, status=status.HTTP_400_BAD_REQUEST)

#     print(user)
#     return Response({"error": "Server Problem"}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def payment_create(request):
    user = request.user
    payment_save = request.query_params.get('save_payment')
    get_amount = Amount.objects.latest('id')
    amount = 69.99*100
    print("-------------------------------------------------------->Create Payment")
    if payment_save:
        amount = 69.99
    print(amount, "------------------------------Amount")
    fullname = f"{user.first_name} {user.last_name}"
    profile = Profile.objects.get(user=user)
    payment_method = PaymentMethod.objects.get(profile=profile)
    print(payment_method, "------------------------------->")
    customer_id = payment_method.stripe_customer_id
    payment_type = profile.payment_type
    if customer_id is not None and len(customer_id) > 0:
        print("---------------------------------------------<")
        charge_customer(customer_id, payment_type)
        # pass
    else:
        customer = stripe.Customer.create(name=fullname,
                                        email=user.email)
        customer_id = customer['id']
        payment_method.stripe_customer_id = customer_id
        payment_method.save()
        print(payment_method, "------------------------------->")

    try:
        intent = stripe.PaymentIntent.create(
            customer=customer_id,
            setup_future_usage='off_session',
            amount = amount,
            currency='usd',
            automatic_payment_methods={
                'enabled': False,
            },
        )
        # print(intent['payment_method_types'][0], "Payment Method--------------------------------->")
        return Response({
            'clientSecret': intent['client_secret'],
            'publishable_key': publish_key
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    # else:
    #     charge_customer(customer_id)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def save_payment(request):
    user = request.user
    profile = Profile.objects.get(user=user)
    payment_method = PaymentMethod.objects.get(profile=profile)
    customer_id = payment_method.stripe_customer_id
    payment_type = profile.payment_type

    if customer_id is not None and len(customer_id) > 0:
        print("---------------------------------------------<")
        payment_methods = stripe.PaymentMethod.list(
                customer=customer_id,
                type=payment_type
            )
        # Charge the customer and payment method immediately
        print("----------------------------------------->")
        card_info = payment_methods['data'][0]['card']
        exp_month = card_info['exp_month']
        exp_year = card_info['exp_year']
        last4 = card_info['last4']
        print(exp_month, exp_year, last4)
        payment_method.last4 = last4
        payment_method.exp_month = exp_month
        payment_method.exp_year = exp_year
        payment_method.save()
    return Response({"message": "Processing..."}, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def remove_payment(request):
    user = request.user
    profile = Profile.objects.get(user=user)
    payment_method = PaymentMethod.objects.get(profile=profile)
    payment_method.stripe_customer_id = None
    payment_method.last4 = ""
    payment_method.exp_month = 0
    payment_method.exp_year = 0
    payment_method.save()
    return Response({"message": "Card Remove Successfully"}, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def unpaid_order_payment(request, order_id):
    user = request.user
    data = request.data
    error = []
    profile = Profile.objects.get(user=user)
    payment_method = PaymentMethod.objects.get(profile=profile)
    payment_type = profile.payment_type
    payment_intent_id = "demo_video"
    payment_method_id = profile.payment_method_id
    if payment_method.stripe_customer_id == None or len(payment_method.stripe_customer_id) == 0:
        if 'payment_intent_id' not in data:
            error.append({"error": "enter your payment intent id"})
        
        if 'payment_method_id' not in data:
            error.append({"error": "enter your payment method id"})
        
        if 'payment_type' not in data:
                error.append({"error": "enter your payment type"})
    
    if len(error) > 0:
        return Response(error, status=status.HTTP_400_BAD_REQUEST)
    
    if 'payment_method_id' and 'payment_intent_id'  and 'payment_type'  in data:
        payment_method_id = data['payment_method_id']
        payment_intent_id = data['payment_intent_id']
        payment_type = data['payment_type']
    order_qs = Order.objects.filter(order_sender__profile=profile, payment_status=False, _id=order_id)
    if not order_qs.exists():
        return Response({"error": "Order Not Exist or Already Paid."}, status=status.HTTP_400_BAD_REQUEST)
    order = order_qs.first()
    video = Video.objects.get(order=order)
    video.privacy_type = 'public'
    video.save()
    order.payment_status = True
    order.status = "completed"
    order.payment_type = payment_type
    order.payment_intent_id = payment_intent_id
    order.save()
    profile.payment_method_id = payment_method_id
    profile.save()

    return Response({
            'message': 'Payment Successfully'
        }, status=status.HTTP_200_OK)

# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def make_payment(request):
#     user = request.user
#     data = request.data
#     get_amount = Amount.objects.latest('id')
#     amount = int(get_amount.amount)
#     profile = Profile.objects.get(user=user)

#     customer_id = profile.stripe_customer_id
#     customer = stripe.Customer.create()
#     payment_type = profile.payment_type
#     if customer_id is not None and len(customer_id) > 0:
#         # charge_customer(customer_id, payment_type)
#         pass
#     else:
#         customer_id = customer['id']

#     try:
#         intent = stripe.PaymentIntent.create(
#             customer=customer_id,
#             setup_future_usage='off_session',
#             amount = amount,
#             currency='usd',
#             automatic_payment_methods={
#                 'enabled': False,
#             },
#         )
#         profile.stripe_customer_id = customer['id']
#         print(intent)
#         profile.save()
#         return Response({
#             'clientSecret': intent['client_secret'],
#             'publishable_key': publish_key
#         }, status=status.HTTP_200_OK)
#     except Exception as e:
#         return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
#     # else:
#     #     charge_customer(customer_id)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def broker_orders(request):
    user = request.user
    this_week = request.query_params.get('week')
    this_month = request.query_params.get('month')
    six_month = request.query_params.get('six_month')
    status_type_query = request.query_params.get('status_type')
    broker_qs = BrokerProfile.objects.filter(profile__user=user)
    if not broker_qs.exists():
        return Response({"error": "Broker Not Exist"}, status=status.HTTP_400_BAD_REQUEST)
    broker = broker_qs.first()
    try:
        orders = Order.objects.all().filter(order_sender=broker).order_by('-created_at')
    except:
        return Response({"error": "Server Error"}, status=status.HTTP_400_BAD_REQUEST)
    if this_week:
        today = datetime.now().date()
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)
        orders = orders.filter(created_at__range=[start_date, end_date])

    if this_month:
        today = datetime.now().date()
        start_date = today.replace(day=1)
        end_date = start_date.replace(day=1, month=start_date.month + 1) - timedelta(days=1)
        orders = orders.filter(created_at__range=[start_date, end_date]).order_by('-created_at')
    if six_month:
        today = datetime.now().date()
        start_date = today - timedelta(days=6*30)
        end_date = today
        orders = orders.filter(created_at__range=[start_date, end_date]).order_by('-created_at')
    if status_type_query:
        orders = orders.filter(status=status_type_query).order_by('-created_at')
    if not orders.exists():
        return Response({"message": "You haven't any order"}, status=status.HTTP_400_BAD_REQUEST)
    return get_paginated_queryset_response(orders, request)


# @api_view(['PUT'])
# @permission_classes([IsAuthenticated])
# def delivery_accept(request, order_id):
#     user = request.user
#     if user.type == "BROKER":
#         broker_qs = BrokerProfile.objects.filter(profile__user=user)
#         if not broker_qs.exists():
#             return Response({"error": "Broker Not Exist"}, status=status.HTTP_400_BAD_REQUEST)
#         broker = broker_qs.first()
#         order_qs = Order.objects.filter(order_sender=broker, _id=order_id, status="video_ready")
#         if not order_qs.exists():
#             return Response({"message": f"{order_id} is not ready"}, status=status.HTTP_200_OK)
#         order = order_qs.first()
#         freelancer = order.order_receiver
#         order.status = "completed"
#         broker.active_orders -= 1
#         broker.total_orders += 1
#         broker.save()
#         freelancer.active_work -= 1
#         freelancer.total_work += 1
#         order.save()
#         freelancer.save()
#         broker_email = broker.profile.email
#         freelancer_email = freelancer.profile.email
#         #Order Complete message to broker and freelancer both mail and notification (template name RealVision Order Completed)
#         return Response({"message": "Order Completed. "}, status=status.HTTP_200_OK)
#     return Response({"error": "You are not Authorize to do this work"}, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def delivery_revisoin(request, order_id):
    user = request.user
    data = request.data
    if user.type == "BROKER":
        broker_qs = BrokerProfile.objects.filter(profile__user=user)
        if 'bug_details' not in data:
            return Response({"error": "enter your bug details"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not broker_qs.exists():
            return Response({"error": "Broker Not Exist"}, status=status.HTTP_400_BAD_REQUEST)
        broker = broker_qs.first()
        order_qs = Order.objects.filter(order_sender=broker, _id=order_id, status="completed")
        if not order_qs.exists():
            return Response({"message": f"you are not eligable for revision"}, status=status.HTTP_400_BAD_REQUEST)
        order = order_qs.first()
        order.status = "in_review"
        order.save()
        BugReport.objects.create(
            order = order,
            bug_details = data['bug_details'],
            is_solve = False
        )
        freelancer = order.order_receiver
        freelancer.bug_rate += 1

        freelancer_user = freelancer.profile.user
        freelancer.save()
        freelander_email = freelancer.profile.email
        broker_email = broker.profile.email
        # Email Send to broker for revision with bug id and also mail admin that broker get review
        title_broker = f"Video Under Review Apologies for the Bug"
        template_broker = "broker_bug_review.html"
        broker_payload = {
            "property_image": order.property_photo_url,
            "report_link": f"{config('DOMAIN')}broker/dashboard"
        }
        try:
            mail_sending(broker_email, broker_payload, template_broker, title_broker)
            print(mail_sending, "-----------------------> mail Sending Broker Bug")
        except Exception as e:
            print(e, "Error On Email On Delivery Revision")
        # Email Send to freelancer that order going for revision with bug id and also mail admin that broker get review
        title = f"Client reported a bug - Please fix it!"
        desc = ""
        notification_type = "alert"
        template = "bug_template.html"
        payload = {
            "property_image": order.property_photo_url,
            "report_link": f"{config('DOMAIN')}editor/review"
        }
        mail_subject = title
        try:
            notification_tem(user, title_broker, desc, notification_type)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        try:
            notification_tem(freelancer_user, title, desc, notification_type)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        try:
            mail_sending(freelander_email, payload, template, mail_subject)
        except Exception as e:
            print(e, "Error on Email on Freelancer on Delivery Revision")
        return Response({"message": "Your Order Going For Revision. "}, status=status.HTTP_200_OK)
    return Response({"error": "You are not Authorize to do this work"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def regenerate_social_text(request, order_id):
    user = request.user
    data = request.data
    if user.type == "BROKER":
        broker_qs = BrokerProfile.objects.filter(profile__user=user)
        if not broker_qs.exists():
            return Response({"error": "Broker Not Exist"}, status=status.HTTP_400_BAD_REQUEST)
        broker = broker_qs.first()
        order_qs = Order.objects.filter(order_sender=broker, _id=order_id, status="completed")
        if not order_qs.exists():
            return Response({"message": f"you are not eligable for revision"}, status=status.HTTP_400_BAD_REQUEST)
        order = order_qs.first()
        
        url = order.url
        prompt = "Create me a short description for a facebook post to present this new property and invite people to share this post and find the new owner for this property in 200 character and don't use any emoji"
        # url = "https://www.dwh.co.uk/campaigns/offers-tailor-made-with-you-in-mind/"
        details_data = f"https://zillow.com{url}"
        try:
            social_media_post = get_details_from_openai(details_data, prompt)
        except:
            social_media_post = None
        order.social_media_post = social_media_post
        order.save()
        return Response({"social_media_post": order.social_media_post}, status=status.HTTP_200_OK)
    return Response({"error": "You are not Authorize to do this work"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def create_order_rating(request, order_id):
    user = request.user
    data = request.data
    if user.type == "BROKER":
        broker_qs = BrokerProfile.objects.filter(profile__user=user)
        if 'rating' not in data:
            return Response({"error": "Please Give Some Rating"}, status=status.HTTP_400_BAD_REQUEST)
        if not broker_qs.exists():
            return Response({"error": "Broker Not Exist"}, status=status.HTTP_400_BAD_REQUEST)
        broker = broker_qs.first()
        order_qs = Order.objects.filter(order_sender=broker, _id=order_id, status__in=["completed","demo"])
        if not order_qs.exists():
            return Response({"error": "your are not authorize or order not eligable for rating"}, status=status.HTTP_400_BAD_REQUEST)
        order = order_qs.first()
        rating = order.rating
        if rating is not None:
            return Response({"error": "Rating already Done. You can't change it again"}, status=status.HTTP_400_BAD_REQUEST)
        order.rating = data['rating']
        order.save()
        return Response({"message": "Thanks for give us ur feedback"}, status=status.HTTP_200_OK)
    else:
        return Response({"error": "You are not Authorize to do that"}, status=status.HTTP_400_BAD_REQUEST)


# -------------------------------------Freelancer Section -----------------------------------

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def accept_order(request, order_id):
    user = request.user
    get_commition = Commition.objects.latest('id')
    commition = int(get_commition.commition)
    qs = FreelancerProfile.objects.filter(profile__user=user)
    if not qs.exists():
        return Response({"message": "freelancer not exist"}, status=status.HTTP_400_BAD_REQUEST)
    freelancer = qs.first()
    if freelancer.status_type == "suspendend":
        return Response({"error": "You are suspended . Please Contact with admin"}, status=status.HTTP_400_BAD_REQUEST)
    order_qs = Order.objects.filter(_id=order_id, status='assigned')
    if not order_qs.exists():
        return Response({"error": "Order not Exist or already on in_process"}, status=status.HTTP_400_BAD_REQUEST)
    order_qs = order_qs.filter(order_receiver=freelancer)
    if not order_qs.exists():
        return Response({"error": "You are not authorize to accept this order"}, status=status.HTTP_400_BAD_REQUEST)
    order = order_qs.first()
    order.status = "in_progress"
    freelancer.pending_earn += int(commition)
    freelancer.save()
    broker_mail = order.order_sender.profile.email
    order.save()

    broker = order.order_sender
    broker_user = broker.profile.user
    #changes=============================================>
    # notification_tem()
    #mail to sender that order in progress. Hope you get ur work very soon
    payload = {"property_image": order.property_photo_url}
    template = "order_progress.html"
    mail_subject = "Your order in progress"
    title = mail_subject
    desc = "Your order in progress. Hope you get ur work very soon"
    notification_type = 'alert'

    try:
        mail_sending(broker_mail, payload, template, mail_subject)
        print(mail_sending)
    except Exception as e:
        print(e, "Order Prgress Email Problem")

    try:
        notification_tem(broker_user, title, desc, notification_type)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    print(broker_mail)
    return Response({"message": f"Order is now {order.status}"}, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def cancel_order(request, order_id):
    user = request.user
    freelancers = FreelancerProfile.objects.all()
    qs = freelancers.filter(profile__user=user)
    if not qs.exists():
        return Response({"message": "freelancer not exist"}, status=status.HTTP_400_BAD_REQUEST)
    freelancer = qs.first()
    if freelancer.status_type == "suspendend":
        return Response({"error": "You are suspended . Please Contact with admin"}, status=status.HTTP_400_BAD_REQUEST)
    if freelancer is None:
        return Response({"error": "Please wait we are trying to find new freelancer for you"}, status=status.HTTP_400_BAD_REQUEST)
    order_qs = Order.objects.filter(_id=order_id, status='assigned')
    if not order_qs.exists():
        return Response({"error": "Order not Exist or already on in_process"}, status=status.HTTP_400_BAD_REQUEST)
    order_qs = order_qs.filter(order_receiver=freelancer)
    if not order_qs.exists():
        return Response({"error": "You are not authorize to accept this order"}, status=status.HTTP_400_BAD_REQUEST)
    order = order_qs.first()
    print(freelancer.active_work)
    print(type(freelancer.active_work))
    freelancer.active_work -= 1
    order.order_receiver = None
    order.save()
    freelancer.save()
    #send mail on admin and notify him that this receiver cancel an order

    #changes ==============================================
    admins = User.objects.filter(is_superuser=True)
    for admin in admins:
        notification_tem(user=admin, title="Decline Work", desc=f"Freelancer {order.order_sender} is not working", notification_type = 'alert')
        email = admin.email
        payload = {}
        template = "cancel_order.html"
        mail_subject = "Receiver cancel an order"
        try:
            mail_sending(email, payload, template, mail_subject)
        except:
            active_email = "asrafulislamais@gmail.com"
            mail_sending(active_email, payload, template, mail_subject)
    profiles = freelancers.filter(status_type="active", freelancer_status=True)
    # profiles = list(profiles)
    if not profiles.exists():
        return Response({"error": "There is no Data Found For Search"}, status=status.HTTP_400_BAD_REQUEST)
    query = profiles.exclude(profile=freelancer.profile)
    order_assign_profile = auto_detect_freelancer(query)
    # print(query)
    if order_assign_profile is None:
        return Response({"message": "Orcer Cancel Successfully"}, status=status.HTTP_200_OK)
    order.order_receiver = order_assign_profile
    print(order_assign_profile)
    order_assign_profile.active_work += 1
    order_assign_profile.save()
    order.save()
    #Main New order Reciever That he got new work
    freelancer_template = "freelancer_got_task.html"
    freelancer_payload = {
                "property_image": order.property_photo_url,
                "task_link" : f"{config('DOMAIN')}editor/my-tasks"
            }
    new_assigner_mail = order_assign_profile.profile.email
    freelancer_order_mail_subject = f"You got a new task. Please do this work first."
    try:
        mail_sending(new_assigner_mail, freelancer_payload, freelancer_template, freelancer_order_mail_subject)
        print(mail_sending, "Freelancer Mail Sending ................>")
    except Exception as e:
        print(e, "Email Problem on Freelancer New Assign")
    return Response({"message": f"Order Cancel Successfully"}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def freelancer_orders(request):
    user = request.user
    status_type_query = request.query_params.get('status_type') 
    freelancer_qs = FreelancerProfile.objects.filter(profile__user=user)
    if not freelancer_qs.exists():
        return Response({"error": "You are not Authorize"}, status=status.HTTP_400_BAD_REQUEST)
    freelancer = freelancer_qs.first()
    orders = Order.objects.all().filter(order_receiver=freelancer)
    if status_type_query:
        orders = orders.filter(status=status_type_query)
    if not orders.exists():
        return Response({"message": "You haven't any order "}, status=status.HTTP_200_OK)
    return get_paginated_queryset_response(orders, request)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def freelancer_payment_remove(request):
    user = request.user
    freelancer_qs = FreelancerProfile.objects.filter(profile__user=user)
    if not freelancer_qs.exists():
        return Response({'error': "Unauthorize Account"}, status=status.HTTP_400_BAD_REQUEST)
    freelancer = freelancer_qs.first()
    if freelancer.status_type == "suspendend":
        return Response({"error": "You are suspended . Please Contact with admin"}, status=status.HTTP_400_BAD_REQUEST)
    payment_method = FreelancerPaymentMethod.objects.get(freelancer=freelancer)
    payment_method.withdrawal_type = None
    payment_method.crypto_address = None
    payment_method.paypal_email = None   
    freelancer.withdraw_info = None
    freelancer.save()
    payment_method.save()
    return Response({"error": "Remove Successfully"}, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def freelancer_payment_save(request):
    user = request.user
    data = request.data
    freelancer_qs = FreelancerProfile.objects.filter(profile__user=user)
    if not freelancer_qs.exists():
        return Response({'error': "Unauthorize Account"}, status=status.HTTP_400_BAD_REQUEST)
    if 'withdrawal_type' not in data:
        return Response({"error": "enter your withdrawal type"}, status=status.HTTP_400_BAD_REQUEST)
    withdrawal_type = data['withdrawal_type']
    if withdrawal_type == "paypal":
        if 'paypal_email' not in data:
            return Response({"error": "enter your paypal email"}, status=status.HTTP_400_BAD_REQUEST)
    elif withdrawal_type== "crypto":
        if 'crypto_address' not in data:
           return Response({"error": "enter your crypto address"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"error": "Please Select Correct Type"}, status=status.HTTP_400_BAD_REQUEST)
    freelancer = freelancer_qs.first()
    if freelancer.status_type == "suspendend":
        return Response({"error": "You are suspended . Please Contact with admin"}, status=status.HTTP_400_BAD_REQUEST)
    if freelancer.withdraw_info is not None:
        return Response({"error": "Already Your Payment System Saved"}, status=status.HTTP_400_BAD_REQUEST)
    payment_method = FreelancerPaymentMethod.objects.get(freelancer=freelancer)
    payment_method.withdrawal_type = withdrawal_type
    if payment_method.withdrawal_type is not None:
        freelancer.withdraw_info = withdrawal_type
        freelancer.save()
    if withdrawal_type == "paypal":
        payment_method.paypal_email = data['paypal_email']    
        payment_method.crypto_address = None
    elif withdrawal_type== "crypto":
        payment_method.crypto_address = data['crypto_address']
        payment_method.paypal_email = None    
    payment_method.save()
    serializer = FreelancerPaymentMethodSerializer(payment_method, many=False)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['post'])
@permission_classes([IsAuthenticated])
def withdraw_request(request):
    user = request.user
    data = request.data
    freelancer_qs = FreelancerProfile.objects.filter(profile__user=user)
    if not freelancer_qs.exists():
        return Response({"error": "Now Authorize for withdraw"}, status=status.HTTP_400_BAD_REQUEST)
    freelancer = freelancer_qs.first()
    withdraw_amount = freelancer.total_revenue
    if withdraw_amount == 0:
        return Response({"error": "You are not allow to withdraw money."}, status=status.HTTP_400_BAD_REQUEST)
    withdraw_method = FreelancerPaymentMethod.objects.get(freelancer=freelancer)
    if withdraw_method.withdrawal_type == None:
        return Response({"error": "Please Connect your wallet for withdraw"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        withdraw_create = FreelancerWithdraw.objects.create(
            withdraw_method = withdraw_method,
            withdraw_amount = withdraw_amount
        )
        if withdraw_create:
            freelancer.total_revenue -= withdraw_amount
            freelancer.save()
    except Exception as e:
        print(e, "Withdraw Create Error ------------------->")
        return Response({"error": "Show Problem On Withdraw."}, status=status.HTTP_400_BAD_REQUEST)
    return Response({"message": "Payment Withdraw Successfully"}, status=status.HTTP_200_OK)
    



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_withdraw_request(request):
    user = request.user
    freelancer_qs = FreelancerProfile.objects.filter(profile__user=user)
    if not freelancer_qs.exists():
        return Response({"error": "Not Authorize for withdraw"}, status=status.HTTP_400_BAD_REQUEST)
    freelancer = freelancer_qs.first()
    withdraw_method = FreelancerPaymentMethod.objects.get(freelancer=freelancer)
    withdrawal_list = FreelancerWithdraw.objects.all().filter(withdraw_method=withdraw_method)
    if not withdrawal_list.exists():
        return Response({"error": "You Haven't Any Order Yet"}, status=status.HTTP_400_BAD_REQUEST)
    serializer = FreelancerWithdrawSerializer(withdrawal_list, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def withdraw_request_details(request, id):
    user = request.user
    if user.is_staff == True or user.type == "FREELANCER":
        withdraw_details = FreelancerWithdraw.objects.filter(id=id)
        if user.type == "FREELANCER":
            freelancer_qs = FreelancerProfile.objects.filter(profile__user=user)
            if not freelancer_qs.exists():
                return Response({"error": "Not Authorize for withdraw"}, status=status.HTTP_400_BAD_REQUEST)
            freelancer = freelancer_qs.first()
            withdraw_method = FreelancerPaymentMethod.objects.get(freelancer=freelancer)
            withdraw_details = withdraw_details.filter(withdraw_method=withdraw_method)
        if not withdraw_details.exists():
            return Response({"error": "Details Not Found"}, status=status.HTTP_400_BAD_REQUEST)
        withdraw = withdraw_details.first()
        serializer = FreelancerWithdrawSerializer(withdraw, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response({"error": "You are not Authorize to see this details"}, status=status.HTTP_400_BAD_REQUEST)



# --------------------------------------------------Admin Statistic --------------------------------------

@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_new_broker_status(request):
    user = request.user
    last_week = timezone.now() - timezone.timedelta(days=7)
    brokers = BrokerProfile.objects.filter(created_at__gte=last_week)
    active_brokers = 0
    for broker in brokers:
        active_orders = int(broker.active_orders)
        if active_orders > 0:
            active_brokers = active_brokers + 1
    data = { "new_members": len(brokers)}
    return Response(data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_orders_info(request):
    today = timezone.now().date()
    today_type = request.query_params.get('today_type') 
    last_week = request.query_params.get('week_type') 
    last_month = request.query_params.get('last_month_type') 
    last_six_month = request.query_params.get('six_month_type') 
    all_time = request.query_params.get('all_time')
    days = 6 
    if last_week:
        days = 7
    if last_month:
        days = 30
    if last_six_month:
        days = 30 * 6
    since_time = timezone.now() - timezone.timedelta(days=days)
    if today_type:
        since_time = today
    try:
        orders = Order.objects.all().filter(created_at__gte=since_time)
    except Exception as e:
        print(e)
    brokers = BrokerProfile.objects.filter(created_at__gte=since_time)
    if all_time:
        orders = Order.objects.all()
        brokers = BrokerProfile.objects.all()
    active_brokers = 0
    for broker in brokers:
        order = Order.objects.filter(order_sender=broker)
        if order.exists():
            active_brokers = active_brokers + 1
        else:
            active_orders = int(broker.active_orders)
            if active_orders > 0:
                active_brokers = active_brokers + 1
    total_orders =orders.filter( payment_status=True)
    sold_videos = len(total_orders)
    incomplete_orders = total_orders.exclude(status__in=["completed", "in_review", "demo"])
    pending_videos = len(incomplete_orders)
    total_earning = 0
    for order in total_orders:
        total_earning = total_earning + int(order.amount)
    pending_orders = orders.filter(payment_status=False, status="demo")
    pending_earning = 0
    for pending_order in pending_orders:
        pending_earning = pending_earning + int(pending_order.amount)
    
    data = {"sold_videos": sold_videos, "pending_videos": pending_videos, "total_earning": total_earning, "pending_earning": pending_earning,  "new_clients": active_brokers, "new_members": len(brokers)}
    return Response(data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def today_new_clients_percent(request):
    today = timezone.now().date()
    try:
        brokers = BrokerProfile.objects.filter(created_at__date=today)
    except Exception as e:
        return Response({"error": e}, status=status.HTTP_400_BAD_REQUEST)
    try:
        orders = Order.objects.filter(created_at__date=today)
    except Exception as e:
        print(e)
        return Response({"error": e},status=status.HTTP_400_BAD_REQUEST)
    total_brokers = len(brokers)
    active_brokers = 0
    for broker in brokers:
        order = Order.objects.filter(order_sender=broker)
        if order.exists():
            active_brokers = active_brokers + 1
        else:
            active_orders = int(broker.active_orders)
            if active_orders > 0:
                active_brokers = active_brokers + 1
    if total_brokers == 0:
        total_brokers = 1
    percentage = (active_brokers*100)/float(total_brokers)
    data = {"new_client_percentage": f"{percentage}%", "today_orders": len(orders), "todays_broker": len(brokers)}
    return Response(data, status=status.HTTP_200_OK)


# @api_view(['GET'])
# @permission_classes([IsAdminUser])
# def get_avg_percentage(request):
#     today = timezone.now().date()
#     days = 6
#     month = request.query_params.get('month')
#     if month:
#         days = 30
#     last_week = today - timedelta(days=days)
#     query = """
#         SELECT
#             strftime('%%w', created_at) as day,
#             COUNT(id) as total_orders,
#             COUNT(CASE WHEN payment_status = 1 THEN 1 ELSE NULL END) as total_paid_orders
#         FROM
#             order_order
#         WHERE
#             DATE(created_at) BETWEEN DATE(%s) AND DATE(%s)
#         GROUP BY
#             day
#         ORDER BY
#             day
#     """
#     with connection.cursor() as cursor:
#         cursor.execute(query, [last_week, today])
#         rows = cursor.fetchall()
#     aggregated_data = []
#     for row in rows:
#         day_name = get_day_name(int(row[0]))
#         total_orders = row[1]
#         total_paid_orders = row[2]
#         aggregated_data.append({
#             'day': day_name,
#             'total_orders': total_orders,
#             'total_paid_orders': total_paid_orders
#         })
#     return Response(aggregated_data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_avg_percentage(request):
    today = timezone.now().date()
    days = 6
    month = request.query_params.get('month')
    if month:
        days = 30
        first_day_of_month = today.replace(day=1)
        last_week = first_day_of_month - timedelta(days=7)
    else:
        last_week = today - timedelta(days=days)
    
    query = """
        SELECT
            strftime('%%w', created_at) as day,
            COUNT(id) as total_orders,
            COUNT(CASE WHEN payment_status = 1 THEN 1 ELSE NULL END) as total_paid_orders
        FROM
            order_order
        WHERE
            DATE(created_at) BETWEEN DATE(%s) AND DATE(%s)
        GROUP BY
            day
        ORDER BY
            day
    """
    with connection.cursor() as cursor:
        cursor.execute(query, [last_week, today])
        rows = cursor.fetchall()
    
    aggregated_data = []
    for row in rows:
        day_name = get_day_name(int(row[0]))
        total_orders = row[1]
        total_paid_orders = row[2]
        aggregated_data.append({
            'title': day_name,
            'total_orders': total_orders,
            'total_paid_orders': total_paid_orders
        })
    return Response(aggregated_data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_freelancer_task_info(request):
    user = request.user
    profile_qs = FreelancerProfile.objects.filter(profile__user=user)
    if not profile_qs.exists():
        return Response({"error": "You are not Authorize"}, status=status.HTTP_400_BAD_REQUEST)
    profile = profile_qs.first()
    try:
        orders = Order.objects.all().filter(order_receiver=profile)
    except Exception as e:
        print(e)
        return Response({"error": "Error From Server"}, status=status.HTTP_400_BAD_REQUEST)
    complete_task = orders.filter(status__in=["completed","demo"])
    pending_task = orders.filter(status__in=["assigned", "in_progress", "in_review"])
    bugs = profile.bug_rate
    complete_task_count = len(complete_task)
    if complete_task_count == 0:
        complete_task_count = 1
    bug_rate = float((int(bugs)*100)/complete_task_count)
    rating = []
    work_time_for_all_task = []
    for task in complete_task:
        assign_time = task.order_assign_time
        delivery_time = task.delivery_time
        if assign_time is not None and delivery_time is not None:
            work_time = datetime.combine(date.today(), delivery_time) - datetime.combine(date.today(), assign_time)
            work_time_for_all_task.append(work_time)
        rate = task.rating
        if rate is not None:
            rating.append(rate)
    total_work_time = sum(work_time_for_all_task, timedelta())
    if len(rating) > 0:
        total_rating = sum(rating)
        divide = len(rating)
    else:
        total_rating = 0
        divide = 1
    rating_percent = total_rating/divide
    all_tasks = len(work_time_for_all_task)
    if all_tasks == 0:
        all_tasks = 1

    avg_speed_delivery = total_work_time / all_tasks
    avg_speed_delivery_days = avg_speed_delivery.days
    avg_speed_delivery_hours = (avg_speed_delivery.seconds // 3600) % 24
    avg_speed_delivery_minutes = (avg_speed_delivery.seconds % 3600) // 60
    formatted_duration = f"{avg_speed_delivery_days}d{avg_speed_delivery_hours}h{avg_speed_delivery_minutes}m"
    data = {"complete_task" : len(complete_task), "pending_task": len(pending_task), "avg_speed_delivery":formatted_duration, "bug_rate": bug_rate, "satisfaction_note": rating_percent}
    return Response(data, status=status.HTTP_200_OK)





