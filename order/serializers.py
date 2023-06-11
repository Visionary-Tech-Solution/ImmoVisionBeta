from rest_framework import serializers

from account.serializers.broker import BrokerProfileSerializer
from account.serializers.freelancer import FreelancerProfileSerializer
from order.models import Amount, BugReport, Commition, DiscountCode, Order

from upload_video.serializer import(
    VideoSerializer
)


class OrderSerializer(serializers.ModelSerializer):
    order_sender = BrokerProfileSerializer()
    order_receiver = FreelancerProfileSerializer()
    #upload_video_url = VideoSerializer()
    class Meta:
        model = Order
        fields = '__all__'