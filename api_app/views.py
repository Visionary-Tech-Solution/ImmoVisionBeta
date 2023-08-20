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
def get_list_property(request,zuid):
    
    # user = request.user
    # qs = User.objects.filter(username=user.username)
    # if not qs.exists():
    #     return Response({"error": "Please Register First "})
    # current_user = qs.first()
    # profile = Profile.objects.get(user=current_user)
    
    data = get_data_from_realtor("1859437","https://www.realtor.com/realestateagents/Rhonda-Richie_ANCHORAGE_AK_2202468_150979998")
    data2 = get_data_from_zillow(zuid)
    data+=data2
    print(type(data))
    if data:
        return Response(data, status=status.HTTP_200_OK)
    else:
        return Response({"error":"Something Went Wrong"},status=status.HTTP_400_BAD_REQUEST)
