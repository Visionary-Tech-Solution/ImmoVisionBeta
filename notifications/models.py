from django.db import models
from common.models.base import BaseModel
from django.contrib.auth import get_user_model

User = get_user_model()

class Notification(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_notification", null=True, blank=True)

    title = models.CharField(max_length=250, null=True, blank=True)
    desc = models.TextField(max_length=250, null=True, blank=True)

    def __str__(self):
        return f"{self.pk}.{self.user}({self.title})"


