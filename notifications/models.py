from common.models.base import BaseModel
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

class Notification(BaseModel):
    NOTIFICATION_TYPE_CHOICES = [
        ('security', 'Security'),
        ('alert', 'Alert'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_notification", null=True, blank=True)

    title = models.TextField(null=True, blank=True)
    desc = models.TextField(null=True, blank=True)
    notification_type = models.CharField(max_length=60, choices=NOTIFICATION_TYPE_CHOICES, null=True, blank=True)

    def __str__(self):
        return f"{self.pk}.{self.user}({self.title})"



class NotificationAction(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_notification_alert")
    social_alert = models.BooleanField(default=True)
    video_ready_alert = models.BooleanField(default=True)
    sms_alert = models.BooleanField(default=True)
    blog_post_alert = models.BooleanField(default=True)
    offer_alert = models.BooleanField(default=True)
    ai_document_ready_alert = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.pk}.{self.user}"