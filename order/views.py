import time
from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from account.models import BrokerProfile, FreelancerProfile
from algorithm.auto_detect_freelancer import auto_detect_freelancer
from algorithm.send_mail import mail_sending
from order.models import (Amount, BugReport, Commition, DiscountCode, MaxOrder,
                          Order)
from order.serializers import OrderSerializer

# Create your views here.
User = get_user_model()
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
            #email (Broker) Order Confirm and ur order assign on receiver_name
            #email (Receiver) You got an Order. Please Do This work fast (Order ID pass)
            return pending_order_assign()
    return True
    
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
                deadline = (datetime.combine(datetime.today(), assign_time) + timedelta(hours=1)).time()
                print(f"Assign Time: {assign_time}, Deadline: {deadline}")
                if assign_time <= deadline:
                    previous_freelancer = FreelancerProfile.objects.get(profile=order.order_receiver.profile)
                    query = profiles.exclude(profile=previous_freelancer.profile)
                    new_assign = auto_detect_freelancer(query)
                    #notifiy admin that previous freelancer not work perfectly
                    if previous_freelancer.active_work > 0:
                        previous_freelancer.active_work -= 1
                    else:
                        previous_freelancer.active_work = 0
                    previous_freelancer.save()
                    order.order_receiver = new_assign
                    #notifiy New Receiver that He Got new work by Email 
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


@api_view(['GET'])
@permission_classes([IsAdminUser])
def all_orders(request):
    status_type_query = request.query_params.get('status_type') 
    try:
        orders = Order.objects.all().order_by('-created_at')
    except:
        return Response({"error": "Server Error"}, status=status.HTTP_400_BAD_REQUEST)
    if status_type_query:
        orders = orders.filter(status=status_type_query)
    return get_paginated_queryset_response(orders, request)
    
# -------------------------------------------------Broker Section---------------------------------

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    user = request.user
    data = request.data
    get_amount = Amount.objects.latest('id')
    amount = int(get_amount.amount)
    qs = BrokerProfile.objects.filter(profile__user=user)
    if not qs.exists():
        return Response({"error": "For making order you have to be Broker"}, status=status.HTTP_400_BAD_REQUEST)
    broker = qs.first()
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
        order_assign_profile = None
    else:
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
                broker_profile = order.order_sender
                broker_email = broker_profile.profile.email
                freelancer_email = order_assign_profile.profile.email
                print(freelancer_email)
                broker_profile.active_orders += 1
                print(broker_email)
                #email (Broker) Order Confirm and ur order assign on receiver_name
                #email (Receiver) You got an Order. Please Do This work first (Order ID pass)


                payload = {
                    "order_id":order._id,
                    "order_date":"02/26/21",

                    #billing info
                    "home":"Maria Bergamot",
                    "road_no":"3409 S. Canondale Road",
                    "area":"Chicago, IL 60301",

                    "product_name":"Video Property Teaser",
                    "qty":1,
                    "amount":order.amount,
                    "tax":"6",
                    "order_link":"www.facebook.com"
                }

                #template
                broker_template = "order_completed.html"
                broker_mail_subject = f"Order Confirm and ur order assign on {order_assign_profile.profile.username}"

                
                order_assign_profile.active_work += 1
                broker_profile.save()
                order_assign_profile.save()
                order.order_assign_time = datetime.now().time()
                order.save()


                #broker
                mail_sending(broker_email, payload, broker_template, broker_mail_subject)

                order_assign_profile.active_work += 1
                broker_profile.save()
                order_assign_profile.save()
                order.order_assign_time = datetime.now().time()
                order.save()
        else:
            #email (Broker) Please wait some time . Very Soon We will Assign a freelancer for complete your order
            pass
        serializer = OrderSerializer(order, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except:
        return Response({"error": "Server Problem"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def broker_orders(request):
    user = request.user
    status_type_query = request.query_params.get('status_type')
    broker_qs = BrokerProfile.objects.filter(profile__user=user)
    if not broker_qs.exists():
        return Response({"error": "Broker Not Exist"}, status=status.HTTP_400_BAD_REQUEST)
    broker = broker_qs.first()

    try:
        orders = Order.objects.all().filter(order_sender=broker).order_by('-created_at')
    except:
        return Response({"error": "Server Error"}, status=status.HTTP_400_BAD_REQUEST)
    if status_type_query:
        orders = orders.filter(status=status_type_query)
    if not orders.exists():
        return Response({"message": "You haven't any order"}, status=status.HTTP_400_BAD_REQUEST)
    return get_paginated_queryset_response(orders, request)


# -------------------------------------Freelancer Section -----------------------------------

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def accept_order(request, order_id):
    user = request.user
    qs = FreelancerProfile.objects.filter(profile__user=user)
    if not qs.exists():
        return Response({"message": "freelancer not exist"}, status=status.HTTP_400_BAD_REQUEST)
    freelancer = qs.first()
    order_qs = Order.objects.filter(_id=order_id, status='assigned')
    if not order_qs.exists():
        return Response({"error": "Order not Exist or already on in_process"}, status=status.HTTP_400_BAD_REQUEST)
    order_qs = order_qs.filter(order_receiver=freelancer)
    if not order_qs.exists():
        return Response({"error": "You are not authorize to accept this order"}, status=status.HTTP_400_BAD_REQUEST)
    order = order_qs.first()
    order.status = "in_progress"
    broker_mail = order.order_sender.profile.email
    order.save()
    #mail to sender that order in progress. Hope you get ur work very soon
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
    order_qs = Order.objects.filter(_id=order_id, status='assigned')
    if not order_qs.exists():
        return Response({"error": "Order not Exist or already on in_process"}, status=status.HTTP_400_BAD_REQUEST)
    order_qs = order_qs.filter(order_receiver=freelancer)
    if not order_qs.exists():
        return Response({"error": "You are not authorize to accept this order"}, status=status.HTTP_400_BAD_REQUEST)
    order = order_qs.first()
    freelancer.active_work -= 1
    freelancer.save()
    #send main on admin and notify him that this receiver cancel an order
    profiles = freelancers.filter(status_type="active", freelancer_status=True)
    # profiles = list(profiles)
    if not profiles.exists():
        return Response({"error": "There is no Data Found For Search"}, status=status.HTTP_400_BAD_REQUEST)
    query = profiles.exclude(profile=freelancer.profile)
    order_assign_profile = auto_detect_freelancer(query)
    # print(query)
    order.order_receiver = order_assign_profile
    order_assign_profile.active_work += 1
    order_assign_profile.save()
    order.save()
    #Main New order Reciever That he got new work
    new_assigner_mail = order_assign_profile.profile.email
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
