from rest_framework import serializers

from account.models import FreelancerProfile
from account.serializers.base import ProfileSerializer


class FreelancerProfileSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()
    class Meta:
        model = FreelancerProfile
        fields = '__all__'
