# from authentication.serializers import UserSerializerWithToken


from rest_framework import status
from rest_framework.decorators import api_view, permission_classes

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .api_fetcher import *



@api_view(['GET'])
#@permission_classes([IsAuthenticated])
def get_list_property(request,zuid):
    #user = request.user
    data = get_data_from_zillow(zuid)
    if data:
        return Response(data, status=status.HTTP_200_OK)
    else:
        return Response({"error":"Something Went Wrong"},status=status.HTTP_400_BAD_REQUEST)
