from rest_framework import serializers

from account.serializers.broker import BrokerProfileSerializer
from account.serializers.freelancer import FreelancerProfileSerializer
from order.models import Amount, BugReport, Commition, DiscountCode, Order


class OrderSerializer(serializers.ModelSerializer):
    order_sender = BrokerProfileSerializer()
    order_receiver = FreelancerProfileSerializer()
    class Meta:
        model = Order
        fields = '__all__'