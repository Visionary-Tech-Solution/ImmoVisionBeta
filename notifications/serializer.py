from authentication.serializers.base_auth import UserCreationSerializer
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from .models import Notification, NotificationAction


class notificationSerializer(ModelSerializer):
    user = UserCreationSerializer()
    class Meta:
        model = Notification
        fields = "__all__"


class notificationActionSerializer(ModelSerializer):
    user = UserCreationSerializer()
    class Meta:
        model = NotificationAction
        fields = "__all__"


