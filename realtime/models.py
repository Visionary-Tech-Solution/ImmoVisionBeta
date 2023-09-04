from django.db import models
from authentication.models import User
class Notification(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    msg = models.TextField(max_length=500)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"User: {self.user.email} msg: {self.msg}"