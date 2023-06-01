from rest_framework.serializers import (
    ModelSerializer
)
from rest_framework import (
    serializers
)
from authentication.serializers.base_auth import UserCreationSerializer
from .models import Notification
from django.contrib.auth import get_user_model

class notificationSerializer(ModelSerializer):
    user = UserCreationSerializer()
    class Meta:
        model = Notification
        fields = "__all__"