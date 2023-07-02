from django.contrib import admin
from upload_video.models import Video, VideoWatermarkImage

# Register your models here.
admin.site.register(Video)
admin.site.register(VideoWatermarkImage)
