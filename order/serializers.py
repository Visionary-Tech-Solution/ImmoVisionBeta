from rest_framework import serializers

from account.serializers.broker import BrokerProfileSerializer
from account.serializers.freelancer import FreelancerProfileSerializer
from order.models import Amount, BugReport, Commition, DiscountCode, Order
from upload_video.models import Video
from upload_video.serializer import VideoSerializer


class OrderSerializer(serializers.ModelSerializer):
    order_sender = BrokerProfileSerializer()
    order_receiver = FreelancerProfileSerializer()
    order_video = serializers.SerializerMethodField(read_only=True)
    order_commission = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Order
        fields = '__all__'

    def get_order_video(self, obj):
        order_id = obj._id
        video_qs = Video.objects.filter(order___id=order_id)
        if not video_qs.exists():
            return None
        video = video_qs.first()
        serializer = VideoSerializer(video, many=False)
        return serializer.data
    
    def get_order_commission(self, obj):
        commition_qs = Commition.objects.latest('id')
        commition = int(commition_qs.commition)
        return str(commition)
    

class BugReportSerializer(serializers.ModelSerializer):
    order = OrderSerializer()
    class Meta:
        model = BugReport
        fields = '__all__'


class DiscountCodeSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = DiscountCode
        fields = '__all__'

    def get_user(self, obj):
        return str(obj.user.username)

