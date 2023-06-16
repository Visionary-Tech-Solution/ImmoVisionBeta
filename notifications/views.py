from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializer import(
    notificationSerializer
)
from .models import (
    Notification
)
from rest_framework.permissions import (
    IsAuthenticated
)

from rest_framework_simplejwt.authentication import (
    JWTAuthentication
)



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