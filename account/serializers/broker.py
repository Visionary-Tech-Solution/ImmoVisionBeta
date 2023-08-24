from rest_framework import serializers

from account.models import BrokerProfile, Profile
from account.serializers.base import ProfileSerializer


class BrokerProfileSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()
    class Meta:
        model = BrokerProfile
        fields = '__all__'
