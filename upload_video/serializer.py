from rest_framework import serializers

from .models import Video


class VideoSerializer(serializers.ModelSerializer):
    order_video_file = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Video
        fields = ['video_id', 'video_title', 'privacy_type', 'order_video_file']

    
    def get_order_video_file(self, obj):
        order = obj.order
        payment_status = order.payment_status
        if payment_status == True:
            try:
                file = obj.video_file.url
            except:
                file = None
        else:
            try:
                file = obj.watermark_video_file.url
            except:
                file = None
        return file

