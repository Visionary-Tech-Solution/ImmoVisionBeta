# from authentication.serializers import UserSerializerWithToken
from account.models import (BrokerProfile, FreelancerProfile, Profile,
                            ProfilePicture)
from account.serializers.base import ProfileSerializer
from account.serializers.broker import BrokerProfileSerializer
from account.serializers.freelancer import FreelancerProfileSerializer
from algorithm.auto_detect_freelancer import auto_detect_freelancer
from decouple import config
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.db.models import Q
from django.utils import timezone
from order.views import Order
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

User = get_user_model()
def get_paginated_queryset_response(qs, request, user_type):
    paginator = PageNumberPagination()
    paginator.page_size = 15
    paginated_qs = paginator.paginate_queryset(qs, request)
    total_pages = paginator.page.paginator.num_pages
    if user_type.lower() == "freelancer":
        serializer = FreelancerProfileSerializer(paginated_qs, many=True)
    elif user_type.lower() == "broker":
        serializer = BrokerProfileSerializer(paginated_qs, many=True)
    else:
        serializer = ProfileSerializer(paginated_qs, many=True)
    return paginator.get_paginated_response({
        'total_pages': total_pages,
        'current_page': paginator.page.number,
        'data': serializer.data,
})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile(request):
    user = request.user
    qs = User.objects.filter(username=user.username)
    if not qs.exists():
        return Response({"error": "You are not Authorize to Show this profile"})
    current_user = qs.first()
    profile = Profile.objects.get(user=current_user)
    if current_user.is_staff:
        serializer = ProfileSerializer(profile, many=False)
    elif current_user.type == "BROKER":
        profile = BrokerProfile.objects.get(profile=profile)
        serializer = BrokerProfileSerializer(profile, many=False)
    elif current_user.type == "FREELANCER":
        profile = FreelancerProfile.objects.get(profile=profile)
        serializer = FreelancerProfileSerializer(profile, many=False)
    else:
        return Response({"message": "You are not authorize"}, status=status.HTTP_401_UNAUTHORIZED)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile(request):
    user = request.user
    qs = User.objects.filter(username=user.username)
    if not qs.exists():
        return Response({"error": "You are not Authorize to Show this profile"})
    current_user = qs.first()
    profile = Profile.objects.get(user=current_user)
    if current_user.is_staff:
        serializer = ProfileSerializer(profile, many=False)
    elif current_user.type == "BROKER":
        profile = BrokerProfile.objects.get(profile=profile)
        serializer = BrokerProfileSerializer(profile, many=False)
    elif current_user.type == "FREELANCER":
        profile = FreelancerProfile.objects.get(profile=profile)
        serializer = FreelancerProfileSerializer(profile, many=False)
    else:
        return Response({"message": "You are not authorize"}, status=status.HTTP_401_UNAUTHORIZED)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_all_broker(request):
    alluser = User.objects.all().filter(type="BROKER")
    print(len(alluser))
    for user in alluser:
        user.delete()
    return Response({"message": "All Broker Delete Successfully"}, status=status.HTTP_200_OK)



@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def broker_update_profile(request):
    data = request.data
    user = request.user
    qs = User.objects.filter(username = user.username)
    if not qs.exists():
        return Response({"error": "you are not authorize to update this profile"}, status=status.HTTP_401_UNAUTHORIZED)
    current_user = qs.first()
    first_name = current_user.first_name
    last_name = current_user.last_name

    if 'name' in data:
        name = data['name']
        name_parts = name.split()
        first_name = name_parts[0]
        last_name = " ".join(name_parts[1:])
        if len(name) < 2:
            first_name = current_user.first_name
            last_name = current_user.last_name
    
    password = current_user.password
    if 'password' in data:
        password = make_password(data['password'])
        if len(password) < 2:
            password = current_user.password

    current_user.first_name = first_name
    current_user.last_name = last_name
    current_user.password = password
    current_user.save()
    profile = Profile.objects.get(user=current_user)
    broker = BrokerProfile.objects.get(profile=profile)
    profile_image_url = request.FILES.get('profile_image', profile.profile_pic)
    image_profile = ProfilePicture.objects.get(user=user)

    image_profile.profile_pic = profile_image_url
    image_profile.save()
    profile_pic = profile.profile_pic
    if 'profile_image' in request.FILES:
        profile_pic = f"{config('BACKEND_DOMAIN')}media/{image_profile.profile_pic}"
        print(profile_pic, "--------------------------->")
    address = profile.address
    if 'address' in request.POST:
        address = data['address']
        if len(address) < 2:
            address = profile.address
    
    phone_number = profile.phone_number
    if 'phone_number' in request.POST:
        phone_number = data['phone_number']
        if len(phone_number) < 2:
            phone_number = profile.phone_number
    
    
    real_estate_agency = broker.real_estate_agency
    if 'real_estate_agency' in request.POST:
        real_estate_agency = data['real_estate_agency']
        if len(real_estate_agency) < 2:
            real_estate_agency = broker.real_estate_agency
    
    website = broker.website
    if 'website' in request.POST:
        website = data['website']
        if len(website) < 2:
            website = broker.website
    try:
        profile.profile_pic = profile_pic
        profile.address = address
        profile.phone_number = phone_number
        broker.real_estate_agency = real_estate_agency
        broker.website = website
        profile.save()
        broker.save()
        return Response({"message": "Profile Update Successfully"}, status=status.HTTP_201_CREATED)
    except:
        return Response({"error": "some issue found on server"}, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def freelancer_update_profile(request):
    data = request.data
    user = request.user
    qs = User.objects.filter(username = user.username)
    if not qs.exists():
        return Response({"error": "you are not authorize to update this profile"}, status=status.HTTP_401_UNAUTHORIZED)
    current_user = qs.first()
    profile = Profile.objects.get(user=current_user)
    freelancer = FreelancerProfile.objects.get(profile=profile)
    profile_image_url = request.FILES.get('profile_image', profile.profile_pic)
    image_profile = ProfilePicture.objects.get(user=user)

    image_profile.profile_pic = profile_image_url
    image_profile.save()
    profile_pic = profile.profile_pic
    if 'profile_image' in request.FILES:
        profile_pic = f"{config('BACKEND_DOMAIN')}media/{image_profile.profile_pic}"
        print(profile_pic, "--------------------------->")
    if freelancer.status_type == "suspendend":
        return Response({"error": "You are suspended . Please Contact with admin"}, status=status.HTTP_400_BAD_REQUEST)
    first_name = current_user.first_name
    last_name = current_user.last_name

    if 'name' in request.POST:
        name = data['name']
        name_parts = name.split()
        first_name = name_parts[0]
        last_name = " ".join(name_parts[1:])
        if len(name) < 2:
            first_name = current_user.first_name
            last_name = current_user.last_name
    
    password = current_user.password
    if 'password' in data:
        password = make_password(data['password'])
        if len(password) < 2:
            password = current_user.password

    current_user.first_name = first_name
    current_user.password = password
    current_user.last_name = last_name
    current_user.save()
    address = profile.address
    if 'address' in request.POST:
        address = data['address']
        if len(address) < 2:
            address = profile.address
    
    phone_number = profile.phone_number
    if 'phone_number' in request.POST:
        phone_number = data['phone_number']
        if len(phone_number) < 2:
            phone_number = profile.phone_number
    try:
        profile.profile_pic = profile_pic
        profile.address = address
        profile.phone_number = phone_number
        profile.save()
        return Response({"message": "Profile Update Successfully"}, status=status.HTTP_201_CREATED)
    except:
        return Response({"error": "some issue found on server"}, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_all_freelancer_profile(request):
    active = request.query_params.get('active')
    email_query = request.query_params.get('email')
    name_query = request.query_params.get('name')
    status_type_query = request.query_params.get('status_type')
    freelancer_all = request.query_params.get('all')
    try:
        profiles = FreelancerProfile.objects.all().order_by('-created_at')
    except:
        return Response({"error": "Server Error"}, status=status.HTTP_400_BAD_REQUEST)
    if freelancer_all:
        if freelancer_all.lower() == "true":
            serializer = FreelancerProfileSerializer(profiles, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
    if active:
        if active.lower() == "true":
            profiles = profiles.filter(freelancer_status=True)
        else:
            profiles = profiles.filter(freelancer_status=False)
    if email_query:
        profiles = profiles.filter(profile__email__icontains = email_query.lower())
    if name_query:
        profiles = profiles.filter(profile__user__first_name__startswith=name_query.title())
    if status_type_query:
        profiles = profiles.filter(status_type = status_type_query.lower())
    if not profiles.exists():
        return Response({"error": "There is no Freelancer at this moment"}, status=status.HTTP_400_BAD_REQUEST)
    return get_paginated_queryset_response(profiles, request, user_type = "freelancer")


@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_all_broker_profile(request):
    active_orders_query = request.query_params.get('active_order') 
    email_query = request.query_params.get('email')
    name_query = request.query_params.get('name')
    broker_all = request.query_params.get('all')
    try:
        profiles = BrokerProfile.objects.all().order_by('-created_at')
    except:
        return Response({"error": "Server Error"}, status=status.HTTP_400_BAD_REQUEST)
    if broker_all:
        if broker_all.lower() == "true":
            serializer = BrokerProfileSerializer(profiles, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
    if email_query:
        profiles = profiles.filter(profile__email__icontains = email_query.lower())
    if name_query:
        profiles = profiles.filter(profile__user__first_name__startswith=name_query.title())
    if active_orders_query:
        profiles = profiles.filter(active_orders__gt=0)
    if not profiles.exists():
        return Response({"error": "There is empty Broker list at this moment"}, status=status.HTTP_400_BAD_REQUEST)
    return get_paginated_queryset_response(profiles, request, user_type = "broker")

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_freelancer_status(request):
    user = request.user
    freelancer_qs = FreelancerProfile.objects.filter(profile__user = user)
    if not freelancer_qs.exists():
        return Response({"error": "Freelancer Profile Not Exist"}, status=status.HTTP_200_OK)
    freelancer = freelancer_qs.first()
    if freelancer.status_type == "suspendend":
        return Response({"error": "You are suspended . Please Contact with admin"}, status=status.HTTP_400_BAD_REQUEST)
    if freelancer.status_type == "active":
        freelancer.status_type = "not_available"
    elif freelancer.status_type == "not_available":
        freelancer.status_type = "active"
    elif freelancer.status_type == "terminated":
        freelancer.delete()
    else:
        return Response({"error": "you are not able to do anything bcz you are suspended/terminated"}, status=status.HTTP_400_BAD_REQUEST)
    freelancer.save()
    return Response({"message": f"{user.username}! you are {freelancer.status_type}"}, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAdminUser])
def admin_status_change(request, username):
    user = request.user
    data = request.data
    print(user)
    freelancer_qs = FreelancerProfile.objects.filter(profile__username = username)
    if 'status_type' not in request.POST:
        return Response({"error": "Please Enter Status Type"}, status=status.HTTP_400_BAD_REQUEST)
    if not freelancer_qs.exists():
        return Response({"error": "Freelancer Profile Not Exist"}, status=status.HTTP_200_OK)
    freelancer = freelancer_qs.first()
    orders = Order.objects.filter(Q(order_receiver=freelancer) & Q(status="pending") | Q(status="assigned") | Q(status="in_progress"))
    status_type = data['status_type']
    active_work = freelancer.active_work
    if status_type == "unsuspended":
        status_type = "active"
    elif status_type == "terminated":
        freelancer.delete()
        return Response({"message": "Freelancer Deleted Successfully"}, status=status.HTTP_200_OK)
    elif status_type == "suspended":
         for order in orders:
            order.order_receiver = None
            order.status = "pending"
            active_work = 0
            order.save() 
    freelancer.status_type = status_type
    freelancer.active_work = active_work
    freelancer.save()
    return Response({"message": f"{username}! are {freelancer.status_type}"}, status=status.HTTP_200_OK)





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
    data = {"new_clients": active_brokers, "new_members": len(brokers)}
    return Response(data, status=status.HTTP_200_OK)

