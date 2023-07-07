from account.models import FreelancerProfile
from account.serializers.base import ProfileSerializer
from account.serializers.payment import (FreelancerPaymentMethod,
                                         FreelancerPaymentMethodSerializer)
from rest_framework import serializers


class FreelancerProfileSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()
    withdraw_info = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = FreelancerProfile
        fields = '__all__'

    def get_withdraw_info(self, obj):
        if obj.withdraw_info == None:
            return None
        freelancer_method = FreelancerPaymentMethod.objects.get(freelancer=obj)
        serializer = FreelancerPaymentMethodSerializer(freelancer_method, many=False)
        return serializer.data





