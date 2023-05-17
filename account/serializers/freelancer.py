import json

from account.models import FreelancerProfile, Profile
from account.serializers.base import ProfileSerializer
from authentication.models import User
from rest_framework import serializers


class FreelancerProfileSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()
    class Meta:
        model = FreelancerProfile
        fields = '__all__'
