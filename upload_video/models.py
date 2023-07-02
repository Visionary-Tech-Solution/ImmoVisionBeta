import uuid

from authentication.models import User
from common.models.base import BaseModel
from django.db import models
from order.models import Order


# Create your models here.
class Video(BaseModel):
    PRIVACY_TYPE_CHOICES = [
        ('private', "Private"),
        ('public', "Public"),
    ]
    video_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    video_title = models.CharField(max_length=250, null=True, blank=True)
    video_file = models.FileField(upload_to='orders/videos/', null=True, blank=True, default=None)
    watermark_video_file = models.FileField(upload_to='orders/watermark_videos/', null=True, blank=True, default=None)
    privacy_type = models.CharField(max_length=30, choices=PRIVACY_TYPE_CHOICES, default="private")
    is_demo = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.video_id}"