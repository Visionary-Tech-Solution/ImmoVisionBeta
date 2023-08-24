# from authentication.serializers import UserSerializerWithToken


from rest_framework import status
from rest_framework.decorators import api_view, permission_classes

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .api_fetcher import *

from authentication.models import User
from account.models import Profile

@api_view(['GET'])
#@permission_classes([IsAuthenticated])
def get_list_property(request):
    
    # user = request.user
    # qs = User.objects.filter(username=user.username)
    # if not qs.exists():
    #     return Response({"error": "Please Register First "})
    # current_user = qs.first()
    # profile = Profile.objects.get(user=current_user)
    
    data = get_data_from_realtor("1859437","https://www.realtor.com/realestateagents/Rhonda-Richie_ANCHORAGE_AK_2202468_150979998")
    data2 = get_data_from_zillow("X1-ZUytn1phpg9b7t_5i26a")
    data+=data2
    print(type(data))
    if data:
        return Response(data, status=status.HTTP_200_OK)
    else:
        return Response({"error":"Something Went Wrong"},status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
#@permission_classes([IsAuthenticated])
def get_image_list(request,zpid,origin):

    if origin=="zillow":
        data = get_image_from_zillow(zpid)
    elif origin=="realtor":
        data = get_image_from_realtor('https://www.realtor.com/realestateandhomes-detail/'+zpid)
    else:
        return Response({"error":"Something Went Wrong"},status=status.HTTP_400_BAD_REQUEST)
    if data:
        return Response(data, status=status.HTTP_200_OK)
    else:
        return Response({"error":"Something Went Wrong"},status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
#@permission_classes([IsAuthenticated])
def get_list_property_info(request,zpid,origin):
    
    # user = request.user
    # qs = User.objects.filter(username=user.username)
    # if not qs.exists():
    #     return Response({"error": "Please Register First "})
    # current_user = qs.first()
    # profile = Profile.objects.get(user=current_user)
    
    if origin=='realtor':
        data = get_data_from_realtor("1859437","https://www.realtor.com/realestateagents/Rhonda-Richie_ANCHORAGE_AK_2202468_150979998",zpid=zpid)

    elif origin=='zillow':
        data = get_data_from_zillow("X1-ZUytn1phpg9b7t_5i26a",zpid=zpid)
    else:
        return Response({"error":"Something Went Wrong"},status=status.HTTP_400_BAD_REQUEST)
    print(type(data))
    if data:
        return Response(data, status=status.HTTP_200_OK)
    else:
        return Response({"error":"Something Went Wrong"},status=status.HTTP_400_BAD_REQUEST)